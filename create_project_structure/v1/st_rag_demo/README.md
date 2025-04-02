# ST RAG Demo

An advanced Streamlit application demonstrating Retrieval Augmented Generation (RAG) capabilities with extensive debugging tools, SQL database integration, and data visualization features.

## Overview

This application provides a comprehensive platform for:

1. **Document RAG**: Query PDF and CSV documents using natural language
2. **SQL Integration**: Transform natural language to SQL and query databases
3. **Data Visualization**: Generate visualizations from data based on natural language requests
4. **RAG Debugging**: Examine the entire RAG pipeline from retrieval to generation
5. **AWS Bedrock Support**: Experiment with different LLM providers including AWS Bedrock

## Key Features

### Document Processing
- Upload and process PDFs, CSVs, and SQLite databases
- Automatic document chunking and vectorization
- Metadata extraction and indexing

### Natural Language Query Capabilities
- Question-answering against document content
- Text-to-SQL query generation
- Text-to-visualization generation

### Visualization
- Automatic chart type selection based on data properties
- Support for bar charts, line charts, scatter plots, and tables
- Interactive Plotly visualizations with download capabilities

### RAG Debugging Tools
- View retrieved document chunks
- Examine the exact prompts sent to the LLM
- Analyze metrics about retrieval performance
- Test different chunking parameters
- Review AWS Bedrock API payloads

### AWS Bedrock Integration
- Support for Claude, Titan, and other AWS Bedrock models
- Guardrail parameter debugging
- Region-specific configurations

## Getting Started

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/st_rag_demo.git
cd st_rag_demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following content:
```
OPENAI_API_KEY=your_openai_api_key
# Optional AWS credentials if using Bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
```

### Running the Application

Start the application with:
```bash
streamlit run app.py
```

## Usage

### RAG Q&A Mode
1. Upload PDFs or CSVs
2. Process the documents
3. Ask questions about your documents
4. Optionally enable Debug Mode to see how RAG works

### SQL Assistant Mode
1. Upload a SQLite database file
2. Ask questions about your data or request SQL queries
3. View the generated queries and their results

### Data Visualization Mode
1. Upload a CSV or SQLite database
2. Request visualizations in natural language
3. Interact with and download the generated charts

## Educational Purpose

This application is designed as a teaching tool to help understand:

- How RAG systems retrieve and process information
- The role of chunking and vectorization in document retrieval
- How prompts are constructed and sent to LLMs
- How text-to-SQL and text-to-visualization systems work
- Debugging approaches for LLM-based applications
- AWS Bedrock configuration and guardrail implementation

## Project Structure

```
st_rag_demo/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore file
└── README.md               # This documentation
```

## License

This project is licensed under the Apache License - see the LICENSE file for details.