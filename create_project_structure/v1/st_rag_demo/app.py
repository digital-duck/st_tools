import os
import pandas as pd
import streamlit as st
import tempfile
import json
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from langchain_community.document_loaders import DataFrameLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from dotenv import load_dotenv

# Optional: AWS Bedrock integration if needed
try:
    import boto3
    from langchain_aws import BedrockChat, BedrockEmbeddings
    AWS_BEDROCK_AVAILABLE = True
except ImportError:
    AWS_BEDROCK_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

class DocumentChatbot:
    def __init__(self):
        """Initialize the document chatbot with OpenAI and ChromaDB"""
        # Initialize the OpenAI model
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.2
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Initialize document splitter with default values
        # These can be updated via the UI in debug mode
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        # Store debugging information
        self.last_formatted_prompt = ""
        self.last_retrieved_context = ""
        self.retriever = None
        
        # Initialize storage for documents and metadata
        self.vectorstore = None
        self.documents = []
        self.file_metadata = {}
        self.chat_history = []
        
        # Initialize SQLite related attributes
        self.db_connection = None
        self.db_path = None
        self.sql_database = None
        self.table_info = {}
        self.sql_engine = None
        
    def process_csv(self, file):
        """Process a CSV file and add to documents"""
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Load CSV file into a pandas DataFrame
        df = pd.read_csv(tmp_path)
        
        # Get DataFrame info as a string
        buffer = pd.io.StringIO()
        df.info(buf=buffer)
        df_info = buffer.getvalue()
        
        # Get DataFrame statistics
        df_stats = df.describe().to_string()
        
        # Sample rows from the DataFrame
        df_sample = df.head(5).to_string()
        
        # Create metadata for the DataFrame
        csv_metadata = f"""
        CSV File: {file.name}
        
        DataFrame Information:
        {df_info}
        
        DataFrame Statistics:
        {df_stats}
        
        Sample Data (first 5 rows):
        {df_sample}
        """
        
        # Store metadata
        self.file_metadata[file.name] = csv_metadata
        
        # Convert DataFrame to documents
        loader = DataFrameLoader(df, page_content_column=df.columns[0])
        csv_docs = loader.load()
        
        # Add metadata to documents
        for doc in csv_docs:
            doc.metadata["file_type"] = "csv"
            doc.metadata["file_name"] = file.name
            doc.metadata["file_info"] = csv_metadata
        
        # Add to documents collection
        self.documents.extend(csv_docs)
        
        # Clean up
        os.unlink(tmp_path)
        
        return len(csv_docs)
    
    def process_pdf(self, file):
        """Process a PDF file and add to documents"""
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Load PDF file
        loader = PyPDFLoader(tmp_path)
        pdf_docs = loader.load()
        
        # Create metadata for the PDF
        pdf_metadata = f"""
        PDF File: {file.name}
        Total Pages: {len(pdf_docs)}
        """
        
        # Store metadata
        self.file_metadata[file.name] = pdf_metadata
        
        # Add metadata to documents
        for doc in pdf_docs:
            doc.metadata["file_type"] = "pdf"
            doc.metadata["file_name"] = file.name
            doc.metadata["file_info"] = pdf_metadata
        
        # Add to documents collection
        self.documents.extend(pdf_docs)
        
        # Clean up
        os.unlink(tmp_path)
        
        return len(pdf_docs)
    
    def process_sqlite(self, file):
        """Process a SQLite database file and set up SQL database connection"""
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Store the path for later use
        self.db_path = tmp_path
        
        # Connect to the database
        try:
            self.db_connection = sqlite3.connect(tmp_path)
            
            # Get list of tables
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Get schema for each table
            table_info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # Get sample data (first 5 rows)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                sample_data = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                
                # Store table info
                table_info[table_name] = {
                    "columns": columns,
                    "sample_data": sample_data,
                    "row_count": row_count
                }
            
            # Store table info for later use
            self.table_info = table_info
            
            # Create a LangChain SQLDatabase object
            self.sql_database = SQLDatabase.from_uri(f"sqlite:///{tmp_path}")
            
            # Store database metadata
            db_metadata = f"""
            SQLite Database: {file.name}
            
            Tables:
            """
            
            for table_name, info in table_info.items():
                db_metadata += f"\n- {table_name} ({info['row_count']} rows)"
                db_metadata += "\n  Columns: "
                db_metadata += ", ".join([col[1] for col in info['columns']])
            
            # Add to file metadata
            self.file_metadata[file.name] = db_metadata
            
            # Generate document for each table schema for vectorstore
            for table_name, info in table_info.items():
                columns_desc = "\n".join([f"- {col[1]} ({col[2]})" for col in info['columns']])
                content = f"""
                Table: {table_name}
                Row count: {info['row_count']}
                
                Columns:
                {columns_desc}
                
                Sample data:
                {str(info['sample_data'])}
                """
                
                # Create a document with table schema
                from langchain_core.documents import Document
                doc = Document(
                    page_content=content,
                    metadata={
                        "file_type": "sqlite",
                        "file_name": file.name,
                        "table_name": table_name,
                        "file_info": db_metadata
                    }
                )
                
                # Add to documents collection
                self.documents.append(doc)
            
            return len(tables)
            
        except Exception as e:
            st.error(f"Error processing SQLite file: {str(e)}")
            if self.db_connection:
                self.db_connection.close()
            os.unlink(tmp_path)
            return 0
    
    def build_vectorstore(self):
        """Build the vector store from the processed documents"""
        if not self.documents:
            return False
        
        # Update text splitter with current settings (for debug mode)
        if hasattr(st, 'session_state') and 'chunk_size' in st.session_state and 'chunk_overlap' in st.session_state:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=st.session_state.chunk_size,
                chunk_overlap=st.session_state.chunk_overlap
            )
            
        # Split documents into chunks
        splits = self.text_splitter.split_documents(self.documents)
        
        # Log chunking stats for debugging
        self.chunk_stats = {
            "total_chunks": len(splits),
            "avg_chunk_size": sum(len(d.page_content) for d in splits) / max(1, len(splits)),
            "chunk_size_setting": self.text_splitter.chunk_size,
            "chunk_overlap_setting": self.text_splitter.chunk_overlap
        }
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(splits, self.embeddings)
        
        return True
    
    def setup_chain(self):
        """Set up the retrieval chain"""
        if not self.vectorstore:
            return None
            
        # Create the retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Expose retriever for debugging
        self.retriever = retriever
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions about document data.
            
            Use the following context from the uploaded files to answer the user's question. 
            If you don't know the answer, say that you don't know. 
            Include relevant statistics and insights from the data where appropriate.
            
            Context: {context}
            
            Files metadata: {file_info}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Create the document chain
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Create the retrieval chain
        return create_retrieval_chain(retriever, document_chain)
    
    def get_file_info(self):
        """Get all file information"""
        if not self.file_metadata:
            return "No files have been uploaded yet."
            
        file_info = "Uploaded Files:\n"
        for filename, metadata in self.file_metadata.items():
            file_info += f"\n{metadata}\n"
            
        return file_info
    
    def execute_sql_query(self, query):
        """Execute a SQL query on the connected database"""
        if not self.db_connection:
            return "No database connected. Please upload a SQLite database file."
        
        try:
            # Execute the query
            cursor = self.db_connection.cursor()
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                # Fetch all results
                results = cursor.fetchall()
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                # Return as DataFrame
                df = pd.DataFrame(results, columns=column_names)
                return df
            else:
                # For non-SELECT queries, commit and return affected row count
                self.db_connection.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
                
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def generate_sql_query(self, question):
        """Generate a SQL query based on a natural language question"""
        if not self.sql_database:
            return "No database connected. Please upload a SQLite database file."
        
        try:
            # Create a SQL Chain with the database
            sql_chain = SQLDatabaseChain.from_llm(
                llm=self.llm,
                db=self.sql_database,
                verbose=True
            )
            
            # Generate SQL query
            response = sql_chain.run(question)
            return response
            
        except Exception as e:
            return f"Error generating SQL query: {str(e)}"
    
    def generate_visualization(self, data, chart_type="auto"):
        """Generate a Plotly visualization based on data and chart type"""
        if isinstance(data, str):
            return data  # Return error message if data is a string (error message)
        
        try:
            # Determine the best chart type if auto
            if chart_type == "auto":
                num_columns = sum(pd.api.types.is_numeric_dtype(data[col]) for col in data.columns)
                categorical_columns = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col])]
                
                if len(data) > 20 and num_columns >= 2:
                    chart_type = "scatter"
                elif len(categorical_columns) >= 1 and num_columns >= 1:
                    chart_type = "bar"
                elif num_columns >= 1:
                    chart_type = "line"
                else:
                    chart_type = "table"
            
            # Create visualization based on chart type
            if chart_type == "scatter" and len(data.columns) >= 2:
                numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
                if len(numeric_cols) >= 2:
                    fig = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1])
                    return fig
            
            elif chart_type == "bar" and len(data.columns) >= 2:
                # Find a categorical column and a numeric column
                categorical_cols = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col])]
                numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
                
                if categorical_cols and numeric_cols:
                    fig = px.bar(data, x=categorical_cols[0], y=numeric_cols[0])
                    return fig
            
            elif chart_type == "line" and len(data.columns) >= 2:
                numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
                if len(numeric_cols) >= 1:
                    # Use first column as x if it's datetime or the index
                    if pd.api.types.is_datetime64_any_dtype(data.index):
                        fig = px.line(data, y=numeric_cols[0])
                    else:
                        fig = px.line(data, y=numeric_cols[0], x=data.columns[0])
                    return fig
            
            # Default to table view
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(data.columns)),
                cells=dict(values=[data[col] for col in data.columns])
            )])
            return fig
            
        except Exception as e:
            return f"Error generating visualization: {str(e)}"
    
    def ask(self, question, return_context=False):
        """
        Ask a question about the documents or database
        
        Args:
            question (str): The question to ask
            return_context (bool): Whether to return the retrieval context along with the answer
            
        Returns:
            str or tuple: Just the answer or (answer, context) depending on return_context
        """
        # Check if this is a SQL or visualization query
        sql_keywords = ["sql", "query", "database", "table", "select", "from", "where", "group by", "order by"]
        viz_keywords = ["plot", "chart", "graph", "visualize", "visualization", "show", "display"]
        
        is_sql_query = any(keyword in question.lower() for keyword in sql_keywords) and self.db_connection is not None
        is_viz_query = any(keyword in question.lower() for keyword in viz_keywords) and self.db_connection is not None
        
        if is_sql_query or is_viz_query:
            # This seems to be a SQL or visualization query
            if "write a query" in question.lower() or "generate a query" in question.lower():
                # User wants just the SQL query
                response = {
                    "answer": self.generate_sql_query(question),
                    "query_type": "sql_generation",
                    "retrieved_context": "",
                    "formatted_prompt": ""
                }
            elif is_viz_query:
                # Try to generate SQL and visualization
                sql_response = self.generate_sql_query(question)
                
                # Extract SQL query from the response if possible
                try:
                    # Look for SQL code block
                    if "```sql" in sql_response:
                        sql_parts = sql_response.split("```sql")
                        query = sql_parts[1].split("```")[0].strip()
                    elif "```" in sql_response:
                        sql_parts = sql_response.split("```")
                        query = sql_parts[1].strip()
                    else:
                        # Try to extract SQL query using common patterns
                        query_indicators = ["SELECT ", "SELECT\n", "select ", "select\n"]
                        for indicator in query_indicators:
                            if indicator in sql_response:
                                query_start = sql_response.find(indicator)
                                query = sql_response[query_start:].strip()
                                # Try to find where the query ends
                                if "Here's" in query or "This query" in query:
                                    query = query.split("Here's")[0].strip()
                                if "This query" in query:
                                    query = query.split("This query")[0].strip()
                                break
                        else:
                            query = sql_response
                    
                    # Execute the extracted query
                    data = self.execute_sql_query(query)
                    
                    # Generate visualization
                    viz = self.generate_visualization(data)
                    
                    response = {
                        "answer": sql_response,
                        "query_type": "visualization",
                        "visualization": viz,
                        "data": data if isinstance(data, pd.DataFrame) else None,
                        "query": query,
                        "retrieved_context": "",
                        "formatted_prompt": ""
                    }
                except Exception as e:
                    response = {
                        "answer": f"I encountered an error while trying to create a visualization: {str(e)}\n\nHere's the information I found: {sql_response}",
                        "query_type": "error",
                        "retrieved_context": "",
                        "formatted_prompt": ""
                    }
            else:
                # Execute direct SQL query or get info about the data
                sql_response = self.generate_sql_query(question)
                
                response = {
                    "answer": sql_response,
                    "query_type": "sql_execution",
                    "retrieved_context": "",
                    "formatted_prompt": ""
                }
                
        else:
            # Standard RAG query
            if not self.vectorstore:
                return "Please upload and process documents first."
                
            # Get retrieval chain
            chain = self.setup_chain()
            
            if not chain:
                return "Error setting up the retrieval chain."
            
            # Get retriever directly for debugging with current k value
            k_value = 5  # Default
            if hasattr(st, 'session_state') and 'k_value' in st.session_state:
                k_value = st.session_state.k_value
                
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k_value}
            )
            
            # Get retrieved documents separately 
            retrieved_docs = retriever.get_relevant_documents(question)
            
            # Format the retrieved context as a string for debugging
            retrieved_context = "\n\n---\n\n".join([f"Document {i+1}:\n{doc.page_content}" 
                                                for i, doc in enumerate(retrieved_docs)])
            
            # Get response from chain
            chain_response = chain.invoke({
                "question": question,
                "chat_history": self.chat_history,
                "file_info": self.get_file_info()
            })
            
            # Create formatted prompt text that would be sent to the LLM
            file_info = self.get_file_info()
            formatted_prompt = f"""System: You are a helpful assistant that answers questions about document data.
                
Use the following context from the uploaded files to answer the user's question. 
If you don't know the answer, say that you don't know. 
Include relevant statistics and insights from the data where appropriate.

Context: {retrieved_context}

Files metadata: {file_info}

Human: {question}"""
            
            # Store this formatted prompt for debugging
            self.last_formatted_prompt = formatted_prompt
            self.last_retrieved_context = retrieved_context
            
            response = {
                "answer": chain_response["answer"],
                "query_type": "rag",
                "retrieved_context": retrieved_context,
                "formatted_prompt": formatted_prompt
            }
        
        # Update chat history
        self.chat_history.append(("human", question))
        self.chat_history.append(("ai", response["answer"]))
        
        if return_context:
            return response
        
        return response["answer"]

def main():
    st.set_page_config(page_title="Document Chatbot", page_icon="📄", layout="wide")
    
    st.title("📄 Advanced RAG Chatbot")
    st.subheader("Chat with your Documents, Databases and Visualize Data")
    
    # Initialize session state for chatbot
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = DocumentChatbot()
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for file upload and processing
    with st.sidebar:
        st.header("Upload Files")
        
        uploaded_files = st.file_uploader(
            "Upload CSV, PDF, or SQLite files", 
            type=["csv", "pdf", "db", "sqlite", "sqlite3"], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            process_clicked = st.button("Process Files")
            
            if process_clicked:
                with st.spinner("Processing files..."):
                    doc_count = 0
                    
                    for file in uploaded_files:
                        if file.name.endswith('.csv'):
                            count = st.session_state.chatbot.process_csv(file)
                            st.write(f"Processed {file.name}: {count} records")
                            doc_count += count
                        elif file.name.endswith('.pdf'):
                            count = st.session_state.chatbot.process_pdf(file)
                            st.write(f"Processed {file.name}: {count} pages")
                            doc_count += count
                        elif file.name.endswith(('.db', '.sqlite', '.sqlite3')):
                            count = st.session_state.chatbot.process_sqlite(file)
                            st.write(f"Processed {file.name}: {count} tables")
                            doc_count += count
                    
                    if doc_count > 0:
                        with st.spinner("Building vector database..."):
                            if st.session_state.chatbot.build_vectorstore():
                                st.success(f"Successfully processed {doc_count} document chunks!")
                            else:
                                st.error("Error building the vector database.")
                    else:
                        st.warning("No documents were processed.")
        
        # LLM model selection - could add AWS Bedrock models
        st.sidebar.header("Model Selection")
        model_provider = st.sidebar.selectbox(
            "Select Model Provider",
            ["OpenAI", "AWS Bedrock (Experimental)"]
        )
        
        if model_provider == "OpenAI":
            model_name = st.sidebar.selectbox(
                "Select OpenAI Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            )
            
            if "model_name" not in st.session_state or st.session_state.model_name != model_name:
                st.session_state.model_name = model_name
                st.sidebar.info(f"Model updated to {model_name}. This will apply to future questions.")
                
        elif model_provider == "AWS Bedrock (Experimental)":
            if not AWS_BEDROCK_AVAILABLE:
                st.sidebar.warning(
                    "AWS Bedrock integration requires additional packages. "
                    "Install with: pip install boto3 langchain-aws"
                )
            
            bedrock_model = st.sidebar.selectbox(
                "Select AWS Bedrock Model",
                [
                    "anthropic.claude-v2",
                    "anthropic.claude-3-sonnet-20240229-v1:0",
                    "anthropic.claude-3-haiku-20240307-v1:0",
                    "amazon.titan-text-express-v1"
                ]
            )
            
            if "bedrock_model" not in st.session_state or st.session_state.bedrock_model != bedrock_model:
                st.session_state.bedrock_model = bedrock_model
                st.sidebar.info(f"Model updated to {bedrock_model}. This will apply to future questions.")
            
            # AWS region selection
            aws_region = st.sidebar.selectbox(
                "AWS Region",
                ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-1", "ap-northeast-1"]
            )
            
            if "aws_region" not in st.session_state or st.session_state.aws_region != aws_region:
                st.session_state.aws_region = aws_region
            
        # App mode selection
        st.sidebar.header("App Mode")
        app_mode = st.sidebar.radio(
            "Select Functionality",
            ["RAG Q&A", "SQL Assistant", "Data Visualization"]
        )
        
        if "app_mode" not in st.session_state or st.session_state.app_mode != app_mode:
            st.session_state.app_mode = app_mode
            st.sidebar.info(f"Mode switched to {app_mode}")
            
        # Display helper information based on mode
        if app_mode == "RAG Q&A":
            st.sidebar.markdown("""
            ### RAG Q&A Mode
            Ask questions about your uploaded documents.
            Example questions:
            - What are the main topics in this document?
            - Summarize the key points from all documents.
            - What does the document say about X?
            """)
        elif app_mode == "SQL Assistant":
            st.sidebar.markdown("""
            ### SQL Assistant Mode
            Get help with SQL queries for your database.
            Example questions:
            - Write a query to find all users who signed up in January.
            - How many orders were placed last month?
            - What's the average transaction value by product category?
            """)
        elif app_mode == "Data Visualization":
            st.sidebar.markdown("""
            ### Data Visualization Mode
            Create charts and visualizations from your data.
            Example questions:
            - Show me a bar chart of sales by region.
            - Visualize the trend of user signups over time.
            - Plot the distribution of product prices.
            """)
            
            # Visualization options
            st.sidebar.subheader("Visualization Options")
            viz_type = st.sidebar.selectbox(
                "Default Chart Type",
                ["auto", "bar", "line", "scatter", "pie", "table"]
            )
            if "viz_type" not in st.session_state or st.session_state.viz_type != viz_type:
                st.session_state.viz_type = viz_type
        
        # Advanced RAG configuration section
        st.sidebar.header("RAG Configuration")
        
        # Add a toggle for debug mode
        debug_mode = st.sidebar.checkbox("Debug Mode (Show RAG Context)", value=False)
        
        # Add RAG parameter controls
        if "k_value" not in st.session_state:
            st.session_state.k_value = 5
            
        if "chunk_size" not in st.session_state:
            st.session_state.chunk_size = 1000
            
        if "chunk_overlap" not in st.session_state:
            st.session_state.chunk_overlap = 100
        
        # Add RAG controls when in debug mode
        if debug_mode:
            st.sidebar.subheader("Retrieval Parameters")
            
            # Number of chunks to retrieve
# Number of chunks to retrieve
            new_k = st.sidebar.slider("Number of chunks (k)", 1, 20, st.session_state.k_value)
            if new_k != st.session_state.k_value:
                st.session_state.k_value = new_k
                st.sidebar.info("K value updated. Changes will apply to the next query.")
            
            # Chunk size for text splitter
            new_chunk_size = st.sidebar.slider("Chunk size", 200, 2000, st.session_state.chunk_size)
            if new_chunk_size != st.session_state.chunk_size:
                st.session_state.chunk_size = new_chunk_size
                st.sidebar.warning("Chunk size updated. You'll need to reprocess files for this to take effect.")
            
            # Chunk overlap for text splitter
            new_chunk_overlap = st.sidebar.slider("Chunk overlap", 0, 500, st.session_state.chunk_overlap)
            if new_chunk_overlap != st.session_state.chunk_overlap:
                st.session_state.chunk_overlap = new_chunk_overlap
                st.sidebar.warning("Chunk overlap updated. You'll need to reprocess files for this to take effect.")
        
        st.header("About")
        st.write("""
        This app demonstrates advanced RAG capabilities:
        - Upload CSV, PDF, or SQLite files
        - Process the files to extract information
        - Ask questions about your documents
        - Generate SQL queries from natural language
        - Create data visualizations
        """)
        
        # Add explanation about debug mode
        if debug_mode:
            st.markdown("""
            ### Debug Mode Enabled
            
            In debug mode, you can see:
            - The actual retrieved context chunks
            - The formatted prompt sent to the LLM
            
            This helps you:
            1. Verify if the correct content is being retrieved
            2. Test prompts directly in the OpenAI playground
            3. Understand RAG behavior better
            """)
            
            # Add a section for RAG troubleshooting tips
            with st.expander("RAG Troubleshooting Tips"):
                st.markdown("""
                ### Common RAG Issues and Solutions
                
                - **Irrelevant retrievals**: Try adjusting chunk size and overlap
                - **Missing information**: Increase k (retrieval count)
                - **Hallucinations**: Check if the context actually contains the necessary information
                - **Poor summaries**: Modify the system prompt to be more specific
                
                ### Testing in the Playground
                
                1. Copy the formatted prompt
                2. Paste into OpenAI playground
                3. Compare responses to identify issues with retrieval vs. summarization
                """)
        
        # Check if OpenAI API key is set
        if not openai_api_key:
            st.warning("Please set your OpenAI API key in a .env file or as an environment variable.")
    
    # Add SQL Database info if applicable
    if hasattr(st.session_state.chatbot, 'db_connection') and st.session_state.chatbot.db_connection is not None:
        st.subheader("Connected Database")
        with st.expander("Database Tables"):
            for table_name, info in st.session_state.chatbot.table_info.items():
                st.write(f"**{table_name}** ({info['row_count']} rows)")
                cols = ", ".join([f"{col[1]} ({col[2]})" for col in info['columns']])
                st.write(f"Columns: {cols}")
    
    # Display example prompts based on mode
    st.subheader("Example Questions")
    current_mode = st.session_state.get("app_mode", "RAG Q&A")
    
    if current_mode == "RAG Q&A":
        example_qs = [
            "What are the main topics in the documents?",
            "Summarize the key points from all files.",
            "Compare and contrast the information in the different files."
        ]
    elif current_mode == "SQL Assistant":
        example_qs = [
            "Write a query to list all tables and their row counts.",
            "How would I find the top 5 records sorted by date?",
            "Create a query to calculate the average values grouped by category."
        ]
    else:  # Data Visualization
        example_qs = [
            "Show me a bar chart of counts by category.",
            "Create a line graph showing the trend over time.",
            "Visualize the distribution of values in the main table."
        ]
    
    for q in example_qs:
        if st.button(q):
            prompt = q
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.ask(prompt, return_context=True)
                    
                    # Handle response (simplified, depending on type)
                    if isinstance(response, dict) and "answer" in response:
                        st.markdown(response["answer"])
                        
                        # Show visualization if available
                        if "visualization" in response and isinstance(response["visualization"], go.Figure):
                            st.plotly_chart(response["visualization"], use_container_width=True)
                    else:
                        st.markdown(response)
            
            # Add assistant response to chat history
            if isinstance(response, dict) and "answer" in response:
                st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
            else:
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            # Rerun to update UI
            st.experimental_rerun()
            
    # Chat input with dynamic placeholder based on mode
    chat_placeholder = {
        "RAG Q&A": "Ask a question about your documents",
        "SQL Assistant": "Ask a question about your database or request a SQL query",
        "Data Visualization": "Describe the visualization you want to create"
    }.get(current_mode, "Ask a question...")
    
    if prompt := st.chat_input(chat_placeholder):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.ask(prompt, return_context=True)
                
                # Handle visualization responses
                if isinstance(response, dict) and "query_type" in response:
                    if response["query_type"] == "visualization" and "visualization" in response:
                        # Display the visualization
                        if isinstance(response["visualization"], go.Figure):
                            st.write("Here's the visualization based on your request:")
                            st.plotly_chart(response["visualization"], use_container_width=True)
                            
                            # Show the data table below the chart
                            if response["data"] is not None and isinstance(response["data"], pd.DataFrame):
                                with st.expander("View Data Table"):
                                    st.dataframe(response["data"])
                        
                        # Also display the text explanation
                        st.markdown(response["answer"])
                        
                        # Allow downloading the data
                        if response["data"] is not None and isinstance(response["data"], pd.DataFrame):
                            csv = response["data"].to_csv(index=False)
                            st.download_button(
                                label="Download Data as CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                    elif response["query_type"] in ["sql_generation", "sql_execution"]:
                        # For SQL queries without visualization
                        st.markdown(response["answer"])
                    else:
                        # Standard RAG response
                        st.markdown(response["answer"])
                else:
                    # Fallback for simple string responses
                    st.markdown(response)
                
                # Display debug information if debug mode is enabled
                if debug_mode:
                    # Create tabs for answer and debugging info including AWS Bedrock
                    answer_tab, context_tab, prompt_tab, metrics_tab, bedrock_tab, sql_tab = st.tabs([
                        "Answer", "Retrieved Context", "Full Prompt", "RAG Metrics", "AWS Bedrock", "SQL Debug"
                    ])
                    
                    with answer_tab:
                        if isinstance(response, dict) and "answer" in response:
                            st.markdown(response["answer"])
                        else:
                            st.markdown(response)
                    
                    with context_tab:
                        if isinstance(response, dict) and "retrieved_context" in response:
                            st.text_area("Retrieved Documents", 
                                        response["retrieved_context"], 
                                        height=400)
                        else:
                            st.text("No context retrieved for this query type.")
                    
                    with prompt_tab:
                        if isinstance(response, dict) and "formatted_prompt" in response:
                            st.text_area("Full Prompt for Playground Testing", 
                                        response["formatted_prompt"], 
                                        height=400)
                            
                            # Add a download button for the prompt
                            prompt_text = response["formatted_prompt"]
                            st.download_button(
                                label="Download Prompt as TXT",
                                data=prompt_text,
                                file_name="rag_prompt.txt",
                                mime="text/plain"
                            )
                        else:
                            st.text("No formatted prompt available for this query type.")
                    
                    with metrics_tab:
                        # Show RAG metrics and stats
                        st.subheader("RAG Retrieval Metrics")
                        
                        # Current configuration
                        st.write("### Current Configuration")
                        st.json({
                            "k_value": st.session_state.k_value,
                            "chunk_size": st.session_state.chunk_size,
                            "chunk_overlap": st.session_state.chunk_overlap,
                            "model": "gpt-3.5-turbo"
                        })
                        
                        # Retrieved chunks stats
                        if isinstance(response, dict) and "retrieved_context" in response and response["retrieved_context"]:
                            st.write("### Retrieved Content Stats")
                            chunks = response["retrieved_context"].split("\n\n---\n\n")
                            chunk_lengths = [len(chunk) for chunk in chunks]
                            
                            st.json({
                                "num_chunks_retrieved": len(chunks),
                                "avg_chunk_length": sum(chunk_lengths) / max(1, len(chunk_lengths)),
                                "min_chunk_length": min(chunk_lengths, default=0),
                                "max_chunk_length": max(chunk_lengths, default=0),
                                "total_context_length": len(response["retrieved_context"])
                            })
                            
                            # Display token estimation (rough approximation)
                            total_chars = len(response["formatted_prompt"]) if "formatted_prompt" in response else 0
                            est_tokens = total_chars / 4  # Rough estimation
                            
                            st.write("### Token Estimation")
                            st.write(f"Estimated total tokens: ~{int(est_tokens)}")
                            if est_tokens > 4000:
                                st.warning("Approaching context limit for GPT-3.5-Turbo (4K tokens)")
                                
                            # Context analysis
                            st.write("### Context Relevance")
                            st.write("Check if retrieved chunks actually contain information relevant to the question.")
                        else:
                            st.write("No retrieval metrics available for this query type.")
                    
                    with sql_tab:
                        st.subheader("SQL Query Debugging")
                        
                        if isinstance(response, dict) and "query_type" in response and response["query_type"] in ["sql_generation", "sql_execution", "visualization"]:
                            # Show extracted SQL query if available
                            if "query" in response:
                                st.code(response["query"], language="sql")
                            
                            # Show data preview if available
                            if "data" in response and response["data"] is not None and isinstance(response["data"], pd.DataFrame):
                                st.subheader("Query Results")
                                st.dataframe(response["data"])
                                
                                # Add data statistics
                                with st.expander("Data Statistics"):
                                    st.write(f"Rows: {len(response['data'])}")
                                    st.write(f"Columns: {', '.join(response['data'].columns.tolist())}")
                                    
                                    # Show basic stats for numeric columns
                                    numeric_cols = response['data'].select_dtypes(include=['number']).columns.tolist()
                                    if numeric_cols:
                                        st.write("Numeric Column Statistics:")
                                        st.dataframe(response['data'][numeric_cols].describe())
                        else:
                            st.text("No SQL query executed for this request.")
                    
                    with bedrock_tab:
                        st.subheader("AWS Bedrock API Payload")
# Add model selector for AWS Bedrock
                        bedrock_model = st.selectbox(
                            "AWS Bedrock Model",
                            [
                                "anthropic.claude-v2",
                                "anthropic.claude-v2:1",
                                "anthropic.claude-3-sonnet-20240229-v1:0",
                                "anthropic.claude-3-haiku-20240307-v1:0",
                                "amazon.titan-text-express-v1",
                                "ai21.j2-mid-v1",
                                "cohere.command-text-v14"
                            ]
                        )
                        
                        # Create appropriate AWS Bedrock payload based on selected model
                        if "anthropic" in bedrock_model:
                            # Anthropic Claude format
                            anthropic_prompt = f"\n\nHuman: {response['formatted_prompt'] if 'formatted_prompt' in response else 'No prompt available'}\n\nAssistant:"
                            
                            bedrock_payload = {
                                "prompt": anthropic_prompt,
                                "max_tokens_to_sample": 4096,
                                "temperature": 0.2,
                                "top_k": 250,
                                "top_p": 0.9,
                                "stop_sequences": ["\n\nHuman:"],
                                # Guardrails parameters would go here
                                "anthropic_version": "bedrock-2023-05-31"
                            }
                            
                            # Add guardrails section for Claude
                            st.write("### Guardrails Parameters")
                            st.write("For Claude models, guardrails are included in the request body:")
                            
                            guardrails_enabled = st.checkbox("Enable Content Filtering", value=True)
                            if guardrails_enabled:
                                bedrock_payload["content_filtering"] = {
                                    "enabled": True
                                }
                            
                            # Add system prompt section
                            system_prompt = st.text_area(
                                "System Prompt (Claude 3 models only)",
                                "You are a helpful, harmless, and honest AI assistant that helps users understand documents.",
                                height=100
                            )
                            
                            if "claude-3" in bedrock_model:
                                bedrock_payload = {
                                    "anthropic_version": "bedrock-2023-05-31",
                                    "max_tokens": 4096,
                                    "temperature": 0.2,
                                    "system": system_prompt,
                                    "messages": [
                                        {
                                            "role": "user",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": response['formatted_prompt'].replace("System: ", "") if 'formatted_prompt' in response else "No prompt available"
                                                }
                                            ]
                                        }
                                    ]
                                }
                                
                        elif "titan" in bedrock_model:
                            # Amazon Titan format
                            bedrock_payload = {
                                "inputText": response['formatted_prompt'] if 'formatted_prompt' in response else "No prompt available",
                                "textGenerationConfig": {
                                    "maxTokenCount": 4096,
                                    "temperature": 0.2,
                                    "topP": 0.9,
                                    "stopSequences": []
                                }
                            }
                            
                        elif "ai21" in bedrock_model:
                            # AI21 format
                            bedrock_payload = {
                                "prompt": response['formatted_prompt'] if 'formatted_prompt' in response else "No prompt available",
                                "maxTokens": 4096,
                                "temperature": 0.2,
                                "topP": 0.9,
                                "stopSequences": []
                            }
                            
                        elif "cohere" in bedrock_model:
                            # Cohere format
                            bedrock_payload = {
                                "prompt": response['formatted_prompt'] if 'formatted_prompt' in response else "No prompt available",
                                "max_tokens": 4096,
                                "temperature": 0.2,
                                "p": 0.9,
                                "k": 0,
                                "stop_sequences": []
                            }
                        
                        # Display the AWS SDK code for direct invocation
                        st.write("### AWS Bedrock SDK Invocation Code")
                        
                        bedrock_code = f"""
import boto3
import json

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'  # Change to your region
)

# Create request payload
payload = {json.dumps(bedrock_payload, indent=2)}

# Invoke the model
response = bedrock_runtime.invoke_model(
    modelId='{bedrock_model}',
    body=json.dumps(payload)
)

# Parse and print the response
response_body = json.loads(response['body'].read())
print(response_body)
"""
                        
                        st.code(bedrock_code, language="python")
                        
                        # Display the raw JSON payload
                        st.write("### Raw JSON Payload")
                        st.json(bedrock_payload)
                        
                        # Add guardrail troubleshooting tips
                        st.write("### Guardrail Troubleshooting Tips")
                        st.markdown("""
                        #### Common Issues with AWS Bedrock Guardrails:
                        
                        1. **Model-specific parameters**: Different models require guardrails in different formats
                        2. **SDK version issues**: Make sure you're using the latest AWS SDK
                        3. **Parameter placement**: Guardrails need to be in the correct location in the payload
                        4. **Region availability**: Some guardrail features may only be available in specific regions
                        5. **Permission issues**: Check your IAM permissions include "bedrock:InvokeModelWithResponseStream"
                        
                        #### Validation Steps:
                        
                        1. Call the model directly using this code snippet and verify the response
                        2. Compare with LangChain responses to identify discrepancies
                        3. Check AWS CloudTrail logs for API errors
                        4. Test with minimal prompt and gradually add complexity
                        """)
                        
                        # Add download button for AWS code
                        st.download_button(
                            label="Download AWS Bedrock Code",
                            data=bedrock_code,
                            file_name="aws_bedrock_invocation.py",
                            mime="text/plain"
                        )
        
        # Add assistant response to chat history
        if isinstance(response, dict) and "answer" in response:
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
        else:
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if __name__ == "__main__":
    main()