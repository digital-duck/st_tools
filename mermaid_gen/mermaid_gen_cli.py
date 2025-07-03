#!/usr/bin/env python3
"""
Mermaid-LangGraph Bidirectional Converter
Converts between Mermaid flowcharts and LangGraph Python code using AST parsing and code generation.
"""

import ast
import click
import os
import re
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass


@dataclass
class GraphNode:
    name: str
    function_name: Optional[str] = None


@dataclass
class GraphEdge:
    source: str
    target: str
    condition: Optional[str] = None
    is_conditional: bool = False


@dataclass
class GraphStructure:
    nodes: Dict[str, GraphNode]
    edges: List[GraphEdge]
    entry_point: Optional[str] = None
    end_nodes: Set[str] = None

    def __post_init__(self):
        if self.end_nodes is None:
            self.end_nodes = set()


class LangGraphParser:
    """Parse LangGraph Python code using AST"""
    
    def __init__(self):
        self.graph_structure = GraphStructure(nodes={}, edges=[])
    
    def parse_file(self, filepath: str) -> GraphStructure:
        """Parse a Python file containing LangGraph code"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        self._extract_graph_structure(tree)
        return self.graph_structure
    
    def _extract_graph_structure(self, tree: ast.AST):
        """Extract graph structure from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._process_method_call(node)
    
    def _process_method_call(self, node: ast.Call):
        """Process method calls to extract graph operations"""
        if not hasattr(node.func, 'attr'):
            return
            
        method_name = node.func.attr
        
        if method_name == 'add_node':
            self._extract_add_node(node)
        elif method_name == 'add_edge':
            self._extract_add_edge(node)
        elif method_name == 'add_conditional_edges':
            self._extract_conditional_edges(node)
        elif method_name == 'set_entry_point':
            self._extract_entry_point(node)
    
    def _extract_add_node(self, node: ast.Call):
        """Extract node information from add_node calls"""
        if len(node.args) >= 1:
            node_name = self._get_string_value(node.args[0])
            function_name = None
            if len(node.args) >= 2:
                function_name = self._get_identifier_name(node.args[1])
            
            if node_name:
                self.graph_structure.nodes[node_name] = GraphNode(
                    name=node_name,
                    function_name=function_name
                )
    
    def _extract_add_edge(self, node: ast.Call):
        """Extract edge information from add_edge calls"""
        if len(node.args) >= 2:
            source = self._get_string_value(node.args[0])
            target = self._get_string_value(node.args[1])
            
            if source and target:
                # Handle END constant
                if target == "END":
                    self.graph_structure.end_nodes.add(source)
                else:
                    self.graph_structure.edges.append(
                        GraphEdge(source=source, target=target)
                    )
    
    def _extract_conditional_edges(self, node: ast.Call):
        """Extract conditional edge information"""
        if len(node.args) >= 3:
            source = self._get_string_value(node.args[0])
            # Skip the condition function (args[1])
            mapping = self._extract_dict_mapping(node.args[2])
            
            if source and mapping:
                for condition, target in mapping.items():
                    if target == "END":
                        self.graph_structure.end_nodes.add(source)
                    else:
                        self.graph_structure.edges.append(
                            GraphEdge(
                                source=source,
                                target=target,
                                condition=condition,
                                is_conditional=True
                            )
                        )
    
    def _extract_entry_point(self, node: ast.Call):
        """Extract entry point from set_entry_point calls"""
        if len(node.args) >= 1:
            entry_point = self._get_string_value(node.args[0])
            if entry_point:
                self.graph_structure.entry_point = entry_point
    
    def _get_string_value(self, node: ast.AST) -> Optional[str]:
        """Extract string value from AST node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8 compatibility
            return node.s
        return None
    
    def _get_identifier_name(self, node: ast.AST) -> Optional[str]:
        """Extract identifier name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        return None
    
    def _extract_dict_mapping(self, node: ast.AST) -> Dict[str, str]:
        """Extract dictionary mapping from AST node"""
        mapping = {}
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                key_str = self._get_string_value(key)
                value_str = self._get_string_value(value)
                if key_str and value_str:
                    mapping[key_str] = value_str
        return mapping


class MermaidParser:
    """Parse Mermaid flowchart syntax"""
    
    def parse_file(self, filepath: str) -> GraphStructure:
        """Parse a Mermaid file"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        return self._parse_mermaid_content(content)
    
    def _parse_mermaid_content(self, content: str) -> GraphStructure:
        """Parse Mermaid content and extract graph structure"""
        graph_structure = GraphStructure(nodes={}, edges=[])
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('flowchart') or line.startswith('graph'):
                continue
            
            # Parse different types of connections
            self._parse_mermaid_line(line, graph_structure)
        
        return graph_structure
    
    def _parse_mermaid_line(self, line: str, graph_structure: GraphStructure):
        """Parse a single Mermaid line"""
        # Handle different arrow types and node definitions
        arrow_patterns = [
            r'(\w+)\s*-->\s*(\w+)',  # Simple arrow
            r'(\w+)\s*-->?\|([^|]+)\|\s*(\w+)',  # Arrow with label
            r'(\w+)\s*{\s*([^}]+)\s*}\s*-->?\s*(\w+)',  # Decision node
        ]
        
        # Extract nodes with their types
        node_patterns = [
            r'(\w+)\[([^\]]+)\]',  # Rectangle node
            r'(\w+)\(([^)]+)\)',   # Rounded node
            r'(\w+)\{([^}]+)\}',   # Decision node
        ]
        
        # First, extract node definitions
        for pattern in node_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                node_id, node_label = match
                graph_structure.nodes[node_id] = GraphNode(
                    name=node_label,
                    function_name=node_label if node_label != 'START' and node_label != 'END' else None
                )
        
        # Then extract edges
        for pattern in arrow_patterns:
            match = re.search(pattern, line)
            if match:
                if len(match.groups()) == 2:  # Simple arrow
                    source, target = match.groups()
                    graph_structure.edges.append(GraphEdge(source=source, target=target))
                elif len(match.groups()) == 3:  # Arrow with condition or decision
                    source, condition_or_target, target = match.groups()
                    if condition_or_target:  # Has condition
                        graph_structure.edges.append(
                            GraphEdge(source=source, target=target, condition=condition_or_target, is_conditional=True)
                        )
                    else:
                        graph_structure.edges.append(GraphEdge(source=source, target=target))


class CodeGenerator:
    """Generate code in both directions"""
    
    @staticmethod
    def generate_mermaid(graph_structure: GraphStructure) -> str:
        """Generate Mermaid flowchart from graph structure"""
        lines = ["flowchart TD"]
        
        # Add entry point
        if graph_structure.entry_point:
            lines.append(f"    START([START]) --> {graph_structure.entry_point}")
        
        # Add nodes with their shapes
        for node_id, node in graph_structure.nodes.items():
            if node.name in ['START', 'END']:
                continue
            lines.append(f"    {node_id}[{node.name}]")
        
        # Add edges
        conditional_edges = {}
        for edge in graph_structure.edges:
            if edge.is_conditional:
                if edge.source not in conditional_edges:
                    conditional_edges[edge.source] = []
                conditional_edges[edge.source].append(edge)
            else:
                lines.append(f"    {edge.source} --> {edge.target}")
        
        # Add conditional edges with decision nodes
        for source, edges in conditional_edges.items():
            decision_node = f"{source}_decision{{Decision}}"
            lines.append(f"    {source} --> {decision_node}")
            for edge in edges:
                condition_label = edge.condition or edge.target
                lines.append(f"    {decision_node} -->|{condition_label}| {edge.target}")
        
        # Add end connections
        for end_source in graph_structure.end_nodes:
            lines.append(f"    {end_source} --> END([END])")
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_langgraph(graph_structure: GraphStructure) -> str:
        """Generate LangGraph Python code from graph structure"""
        lines = [
            "from langgraph.graph import StateGraph, END",
            "",
            "def create_agent_graph():",
            '    """Generated from Mermaid flowchart"""',
            "",
            "    # Create the workflow graph",
            "    workflow = StateGraph(AgentState)",
            "",
            "    # Add nodes"
        ]
        
        # Add nodes
        for node_id, node in graph_structure.nodes.items():
            if node.function_name and node.name not in ['START', 'END']:
                lines.append(f'    workflow.add_node("{node_id}", {node.function_name})')
        
        lines.extend([
            "",
            "    # Define edges and entry point"
        ])
        
        # Set entry point
        if graph_structure.entry_point:
            lines.append(f'    workflow.set_entry_point("{graph_structure.entry_point}")')
        
        # Group conditional edges by source
        conditional_edges = {}
        simple_edges = []
        
        for edge in graph_structure.edges:
            if edge.is_conditional:
                if edge.source not in conditional_edges:
                    conditional_edges[edge.source] = []
                conditional_edges[edge.source].append(edge)
            else:
                simple_edges.append(edge)
        
        # Add simple edges
        for edge in simple_edges:
            lines.append(f'    workflow.add_edge("{edge.source}", "{edge.target}")')
        
        # Add conditional edges
        for source, edges in conditional_edges.items():
            mapping = {edge.condition or edge.target: edge.target for edge in edges}
            mapping_str = "{\n" + ",\n".join([f'        "{k}": "{v}"' for k, v in mapping.items()]) + "\n    }"
            lines.extend([
                f'    workflow.add_conditional_edges(',
                f'        "{source}",',
                f'        lambda x: x["next"],  # TODO: Implement routing logic',
                f'        {mapping_str}',
                f'    )'
            ])
        
        # Add end connections
        for end_source in graph_structure.end_nodes:
            lines.append(f'    workflow.add_edge("{end_source}", END)')
        
        lines.extend([
            "",
            "    # Compile the graph",
            "    return workflow.compile()  # TODO: Add checkpointer if needed"
        ])
        
        return '\n'.join(lines)


def validate_consistency(py_graph: GraphStructure, mermaid_graph: GraphStructure) -> Tuple[bool, List[str]]:
    """Validate consistency between Python and Mermaid representations"""
    issues = []
    
    # Check nodes
    py_nodes = set(py_graph.nodes.keys())
    mermaid_nodes = set(mermaid_graph.nodes.keys())
    
    if py_nodes != mermaid_nodes:
        missing_in_mermaid = py_nodes - mermaid_nodes
        missing_in_py = mermaid_nodes - py_nodes
        if missing_in_mermaid:
            issues.append(f"Nodes missing in Mermaid: {missing_in_mermaid}")
        if missing_in_py:
            issues.append(f"Nodes missing in Python: {missing_in_py}")
    
    # Check edges (simplified check)
    py_edge_pairs = {(e.source, e.target) for e in py_graph.edges}
    mermaid_edge_pairs = {(e.source, e.target) for e in mermaid_graph.edges}
    
    if py_edge_pairs != mermaid_edge_pairs:
        issues.append("Edge structures differ between Python and Mermaid")
    
    return len(issues) == 0, issues


@click.command()
@click.option('--py', help='Path to Python LangGraph file')
@click.option('--mermaid', help='Path to Mermaid flowchart file')
def main(py, mermaid):
    """
    Bidirectional converter between Mermaid flowcharts and LangGraph Python code.
    
    Usage examples:
    - Generate Mermaid from Python: python mermaid_gen.py --py graph.py --mermaid graph.mermaid
    - Generate Python from Mermaid: python mermaid_gen.py --py graph.py --mermaid graph.mermaid
    - Validate consistency: python mermaid_gen.py --py existing.py --mermaid existing.mermaid
    """
    
    py_exists = py and os.path.exists(py)
    mermaid_exists = mermaid and os.path.exists(mermaid)
    
    if not py and not mermaid:
        click.echo("Error: Must specify at least one of --py or --mermaid")
        click.echo(main.get_help(click.Context(main)))
        return
    
    if not py_exists and not mermaid_exists:
        click.echo("Error: At least one input file must exist")
        click.echo(main.get_help(click.Context(main)))
        return
    
    try:
        if py_exists and mermaid_exists:
            # Both exist - validate consistency
            click.echo("Both files exist. Performing consistency check...")
            
            py_parser = LangGraphParser()
            py_graph = py_parser.parse_file(py)
            
            mermaid_parser = MermaidParser()
            mermaid_graph = mermaid_parser.parse_file(mermaid)
            
            is_consistent, issues = validate_consistency(py_graph, mermaid_graph)
            
            if is_consistent:
                click.echo("✅ Files are consistent!")
            else:
                click.echo("❌ Consistency issues found:")
                for issue in issues:
                    click.echo(f"  - {issue}")
        
        elif py_exists and not mermaid_exists:
            # Generate Mermaid from Python
            click.echo(f"Generating Mermaid file from {py}...")
            
            parser = LangGraphParser()
            graph_structure = parser.parse_file(py)
            
            mermaid_code = CodeGenerator.generate_mermaid(graph_structure)
            
            with open(mermaid, 'w') as f:
                f.write(mermaid_code)
            
            click.echo(f"✅ Generated {mermaid}")
        
        elif mermaid_exists and not py_exists:
            # Generate Python from Mermaid
            click.echo(f"Generating Python file from {mermaid}...")
            
            parser = MermaidParser()
            graph_structure = parser.parse_file(mermaid)
            
            python_code = CodeGenerator.generate_langgraph(graph_structure)
            
            with open(py, 'w') as f:
                f.write(python_code)
            
            click.echo(f"✅ Generated {py}")
    
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        raise


if __name__ == '__main__':
    main()