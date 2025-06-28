#!/usr/bin/env python3
"""
Python & SQL Code Validator
===========================

Focused validator for Machine Learning Engineers and Data Engineers.
Validates Python (including data science libraries) and SQL code with
domain-specific checks and auto-fixes.

Usage:
    python py_sql_validator.py                     # Interactive mode
    python py_sql_validator.py validate script.py  # Validate Python
    python py_sql_validator.py validate query.sql  # Validate SQL
    python py_sql_validator.py batch "src/**/*.py" # Batch validate
    
Features:
- Python AST-based validation with data science focus
- SQL syntax validation and formatting
- Auto-fix common issues (nested quotes, indentation, SQL formatting)
- Safety checks for data processing code
- Integration-ready for code generation workflows
"""

import ast
import re
import json
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import click


class Language(Enum):
    PYTHON = "python"
    SQL = "sql"


class ValidationResult(Enum):
    VALID = "valid"
    SYNTAX_ERROR = "syntax_error"
    FIXED = "fixed"
    UNSUPPORTED = "unsupported"


@dataclass
class CodeIssue:
    line_number: int
    column: int
    message: str
    error_type: str
    suggested_fix: Optional[str] = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    language: Language
    result: ValidationResult
    is_valid: bool
    issues: List[CodeIssue]
    original_code: str
    fixed_code: Optional[str] = None
    ast_tree: Optional[Any] = None
    execution_safe: bool = False


class PythonSQLValidator:
    """Validator for Python and SQL code"""
    
    def __init__(self, auto_fix: bool = True, strict_mode: bool = False):
        self.auto_fix = auto_fix
        self.strict_mode = strict_mode
    
    def detect_language(self, code: str, filename: str = "") -> Language:
        """Auto-detect Python vs SQL"""
        if filename:
            ext = Path(filename).suffix.lower()
            if ext == '.sql':
                return Language.SQL
            elif ext in ['.py', '.pyi']:
                return Language.PYTHON
        
        # SQL keywords detection
        sql_keywords = r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|FROM|WHERE|JOIN)\b'
        if re.search(sql_keywords, code, re.IGNORECASE):
            return Language.SQL
        
        return Language.PYTHON
    
    def validate_code(self, code: str, language: Optional[Language] = None, filename: str = "") -> ValidationReport:
        """Validate code"""
        if language is None:
            language = self.detect_language(code, filename)
        
        if language == Language.PYTHON:
            return self._validate_python(code, filename)
        elif language == Language.SQL:
            return self._validate_sql(code, filename)
        else:
            return ValidationReport(
                language=language,
                result=ValidationResult.UNSUPPORTED,
                is_valid=False,
                issues=[CodeIssue(0, 0, f"Language {language.value} not supported", "UnsupportedLanguage")],
                original_code=code
            )
    
    def _validate_python(self, code: str, filename: str) -> ValidationReport:
        """Validate Python code with data science focus"""
        issues = []
        fixed_code = None
        ast_tree = None
        result = ValidationResult.SYNTAX_ERROR
        
        try:
            # Parse with AST
            ast_tree = ast.parse(code, filename=filename)
            result = ValidationResult.VALID
            is_valid = True
            
            # Data science specific checks
            if self.strict_mode:
                issues.extend(self._data_science_checks(ast_tree, code))
                
        except SyntaxError as e:
            issue = CodeIssue(
                line_number=e.lineno or 0,
                column=e.offset or 0,
                message=f"Syntax Error: {e.msg}",
                error_type="SyntaxError"
            )
            issues.append(issue)
            
            # Auto-fix attempts
            if self.auto_fix:
                fixed_code, fix_successful = self._fix_python_code(code, filename)
                if fix_successful:
                    try:
                        ast_tree = ast.parse(fixed_code, filename=filename)
                        result = ValidationResult.FIXED
                        is_valid = True
                        issues.append(CodeIssue(0, 0, "Auto-fixed Python code", "AutoFix", severity="info"))
                    except SyntaxError:
                        is_valid = False
                else:
                    is_valid = False
            else:
                is_valid = False
                
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"Parsing Error: {str(e)}", type(e).__name__))
            is_valid = False
        
        execution_safe = self._check_python_safety(code) if is_valid else False
        
        return ValidationReport(
            language=Language.PYTHON,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            ast_tree=ast_tree,
            execution_safe=execution_safe
        )
    
    def _validate_sql(self, code: str, filename: str) -> ValidationReport:
        """Validate SQL code"""
        issues = []
        result = ValidationResult.VALID
        is_valid = True
        fixed_code = None
        
        try:
            # Try sqlparse if available
            try:
                import sqlparse
                
                parsed = sqlparse.parse(code)
                
                # SQL validation checks
                for statement in parsed:
                    if not statement.tokens:
                        continue
                    
                    sql_text = str(statement).strip()
                    if not sql_text:
                        continue
                    
                    # Check for valid SQL patterns
                    issues.extend(self._validate_sql_statement(statement))
                
                # Auto-format SQL
                if self.auto_fix:
                    formatted = sqlparse.format(
                        code, 
                        reindent=True, 
                        keyword_case='upper',
                        identifier_case='lower'
                    )
                    if formatted != code:
                        fixed_code = formatted
                        result = ValidationResult.FIXED
                        issues.append(CodeIssue(0, 0, "SQL formatted", "AutoFormat", severity="info"))
                
            except ImportError:
                issues.append(CodeIssue(0, 0, "sqlparse not available - install with: pip install sqlparse", 
                                      "MissingDependency", severity="warning"))
                is_valid = self._basic_sql_validation(code, issues)
                
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"SQL validation error: {str(e)}", "ValidationError"))
            is_valid = False
            result = ValidationResult.SYNTAX_ERROR
        
        return ValidationReport(
            language=Language.SQL,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=True
        )
    
    def _fix_python_code(self, code: str, filename: str) -> Tuple[str, bool]:
        """Auto-fix Python code issues"""
        fixes = [
            self._fix_nested_quotes,
            self._fix_indentation,
            self._fix_imports,
            self._fix_encoding
        ]
        
        current_code = code
        for fix_func in fixes:
            try:
                fixed = fix_func(current_code)
                if fixed != current_code:
                    try:
                        ast.parse(fixed, filename=filename)
                        return fixed, True
                    except SyntaxError:
                        current_code = fixed
                        continue
            except:
                continue
        
        return current_code, False
    
    def _fix_nested_quotes(self, code: str) -> str:
        """Fix meta-programming quote issues - specifically for code generation"""
        
        # The REAL problem pattern:
        # return '''"""  -> the ''' gets replaced with """ creating """"""
        # 
        # CORRECT approach: Use different outer quotes entirely
        
        lines = code.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Main fix: Handle "return '''" followed by content
            if line.strip() == "return '''":
                # This is the start of a multiline string return
                # Change to triple double quotes
                fixed_lines.append(line.replace("return '''", 'return """'))
                i += 1
                
                # Process the content between the quotes
                while i < len(lines):
                    content_line = lines[i]
                    
                    # Check if this is the closing line
                    if content_line.strip() == "'''":
                        # Change closing quotes to match
                        fixed_lines.append(content_line.replace("'''", '"""'))
                        break
                    else:
                        # This is content inside - convert docstring quotes to avoid conflicts
                        if content_line.strip().startswith('"""') and content_line.strip().endswith('"""'):
                            # This is a docstring line - convert to single quotes
                            content_line = content_line.replace('"""', "'''")
                        elif '"""' in content_line:
                            # Partial docstring quotes - convert them
                            content_line = content_line.replace('"""', "'''")
                        
                        fixed_lines.append(content_line)
                    i += 1
            
            # Handle inline return statements: return '''content'''
            elif line.strip().startswith("return '''") and line.rstrip().endswith("'''"):
                # This is a single-line return with triple quotes
                # Extract the content
                content = line[line.find("return '''") + 10:line.rfind("'''")]
                # Fix any inner quotes
                content = content.replace('"""', "'''")
                # Reconstruct with proper quotes
                indent = line[:line.find("return")]
                fixed_line = f'{indent}return """{content}"""'
                fixed_lines.append(fixed_line)
            
            # Emergency cleanup: fix any existing 4+ quote sequences
            elif "''''" in line or '""""' in line:
                line = re.sub(r"'{4,}", "'''", line)
                line = re.sub(r'"{4,}', '"""', line)
                fixed_lines.append(line)
            
            else:
                fixed_lines.append(line)
            
            i += 1
        
        code = '\n'.join(fixed_lines)
        
        # Final cleanup for f-strings
        def fix_fstring_quotes(match):
            content = match.group(2)
            if '"' in content and "'" not in content:
                return f"f'{content}'"
            elif "'" in content and '"' not in content:
                return f'f"{content}"'
            return match.group(0)
        
        code = re.sub(r'f(["\'])(.*?)\1', fix_fstring_quotes, code)
        
        return code
    
    def _fix_indentation(self, code: str) -> str:
        """Fix Python indentation"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Convert tabs to 4 spaces
            fixed_line = line.expandtabs(4)
            
            # Fix non-standard indentation
            if fixed_line.lstrip() != fixed_line:
                leading_spaces = len(fixed_line) - len(fixed_line.lstrip())
                if leading_spaces % 4 != 0:
                    new_spaces = ((leading_spaces + 2) // 4) * 4
                    fixed_line = ' ' * new_spaces + fixed_line.lstrip()
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_imports(self, code: str) -> str:
        """Fix common import issues"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix common data science import patterns
            if 'import pandas as pd' in line and 'pd' not in line:
                line = line.replace('import pandas', 'import pandas as pd')
            elif 'import numpy as np' in line and 'np' not in line:
                line = line.replace('import numpy', 'import numpy as np')
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_encoding(self, code: str) -> str:
        """Fix encoding issues"""
        replacements = {
            '"': '"', '"': '"',  # Smart quotes
            ''': "'", ''': "'",
            '–': '-', '—': '--'
        }
        for old, new in replacements.items():
            code = code.replace(old, new)
        return code
    
    def _data_science_checks(self, ast_tree: ast.AST, code: str) -> List[CodeIssue]:
        """Data science specific validation"""
        issues = []
        
        class DataScienceVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.has_pandas = 'pandas' in code or 'pd.' in code
                self.has_numpy = 'numpy' in code or 'np.' in code
            
            def visit_Call(self, node):
                # Check for common pandas performance issues
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'pd' and 
                        node.func.attr == 'concat'):
                        
                        # Check if concat is in a loop (common anti-pattern)
                        parent = getattr(node, 'parent', None)
                        if self._is_in_loop(node):
                            self.issues.append(CodeIssue(
                                line_number=node.lineno,
                                column=node.col_offset,
                                message="pd.concat() in loop - consider using list and concat once",
                                error_type="PerformanceWarning",
                                severity="warning",
                                suggested_fix="Collect DataFrames in list, then pd.concat(list)"
                            ))
                
                # Check for dangerous eval/exec
                if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        message=f"Dangerous function: {node.func.id}",
                        error_type="SecurityWarning",
                        severity="warning"
                    ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for data science imports
                for alias in node.names:
                    if alias.name in ['pandas', 'numpy', 'sklearn', 'tensorflow', 'torch']:
                        if not alias.asname:
                            common_aliases = {
                                'pandas': 'pd',
                                'numpy': 'np',
                                'tensorflow': 'tf'
                            }
                            if alias.name in common_aliases:
                                self.issues.append(CodeIssue(
                                    line_number=node.lineno,
                                    column=node.col_offset,
                                    message=f"Consider using standard alias: import {alias.name} as {common_aliases[alias.name]}",
                                    error_type="StyleSuggestion",
                                    severity="info"
                                ))
                self.generic_visit(node)
            
            def _is_in_loop(self, node):
                """Check if node is inside a loop"""
                # This is simplified - in practice you'd walk up the AST
                return 'for ' in code or 'while ' in code
        
        visitor = DataScienceVisitor()
        visitor.visit(ast_tree)
        return visitor.issues
    
    def _check_python_safety(self, code: str) -> bool:
        """Check Python safety for data processing"""
        dangerous_patterns = [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bos\.system\s*\(',
            r'\bsubprocess\.',
            r'\bopen\s*\([^)]*[\'"][wa]',  # File writing
            r'\.to_sql\s*\([^)]*if_exists\s*=\s*[\'"]replace[\'"]'  # SQL table replacement
        ]
        return not any(re.search(pattern, code, re.IGNORECASE) for pattern in dangerous_patterns)
    
    def _validate_sql_statement(self, statement) -> List[CodeIssue]:
        """Validate individual SQL statement"""
        issues = []
        sql_text = str(statement).strip().upper()
        
        # Check for common SQL issues
        if 'SELECT *' in sql_text:
            issues.append(CodeIssue(
                line_number=1,
                column=0,
                message="SELECT * can be inefficient - consider specifying columns",
                error_type="PerformanceWarning",
                severity="warning",
                suggested_fix="SELECT specific_column1, specific_column2 FROM ..."
            ))
        
        # Check for missing WHERE clause in UPDATE/DELETE
        if sql_text.startswith(('UPDATE', 'DELETE')) and 'WHERE' not in sql_text:
            issues.append(CodeIssue(
                line_number=1,
                column=0,
                message="UPDATE/DELETE without WHERE clause - this affects all rows!",
                error_type="SafetyWarning",
                severity="warning",
                suggested_fix="Add WHERE clause to limit affected rows"
            ))
        
        return issues
    
    def _basic_sql_validation(self, code: str, issues: List[CodeIssue]) -> bool:
        """Basic SQL validation without sqlparse"""
        # Check balanced parentheses
        if code.count('(') != code.count(')'):
            issues.append(CodeIssue(0, 0, "Unbalanced parentheses", "SyntaxError"))
            return False
        
        # Check balanced quotes
        if code.count("'") % 2 != 0 or code.count('"') % 2 != 0:
            issues.append(CodeIssue(0, 0, "Unbalanced quotes", "SyntaxError"))
            return False
        
        return True
    
    def validate_file(self, filepath: Union[str, Path]) -> ValidationReport:
        """Validate a file"""
        filepath = Path(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.validate_code(code, filename=str(filepath))
        except FileNotFoundError:
            return ValidationReport(
                language=Language.PYTHON,
                result=ValidationResult.SYNTAX_ERROR,
                is_valid=False,
                issues=[CodeIssue(0, 0, f"File not found: {filepath}", "FileNotFound")],
                original_code=""
            )


def print_report(report: ValidationReport, verbose: bool = False):
    """Print validation report"""
    click.echo()
    click.echo("="*60)
    click.echo(f"VALIDATION REPORT ({report.language.value.upper()})")
    click.echo("="*60)
    
    status_icon = "✅" if report.is_valid else "❌"
    click.echo(f"Status: {status_icon} {report.result.value.upper()}")
    
    if hasattr(report, 'execution_safe'):
        safety = "🟢 Safe" if report.execution_safe else "🟡 Review needed"
        click.echo(f"Safety: {safety}")
    
    if report.issues:
        click.echo(f"\nIssues ({len(report.issues)}):")
        click.echo("-" * 30)
        
        for issue in report.issues:
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "❓")
            click.echo(f"{icon} Line {issue.line_number}: {issue.message}")
            if issue.suggested_fix:
                click.echo(f"   💡 {issue.suggested_fix}")
    
    if report.fixed_code and verbose:
        click.echo(f"\nFixed Code:")
        click.echo("-" * 30)
        click.echo(report.fixed_code)


def interactive_mode():
    """Interactive validation mode"""
    click.echo("🔍 Python & SQL Code Validator")
    click.echo("Enter code (type 'END' to finish, 'quit' to exit)")
    click.echo("-" * 50)
    
    validator = PythonSQLValidator(auto_fix=True, strict_mode=True)
    
    while True:
        click.echo("\nEnter code:")
        lines = []
        while True:
            line = input(">>> " if not lines else "... ")
            if line.strip() == 'END':
                break
            if line.strip() == 'quit':
                return
            lines.append(line)
        
        if lines:
            code = '\n'.join(lines)
            report = validator.validate_code(code)
            print_report(report, verbose=True)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Python & SQL code validator for ML/Data Engineers."""
    if ctx.invoked_subcommand is None:
        interactive_mode()


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--language', '-l', type=click.Choice(['python', 'sql']), 
              help='Force language detection')
@click.option('--fix/--no-fix', default=True, help='Auto-fix and save (default: enabled)')
@click.option('--strict/--no-strict', default=True, help='Enable data science checks (default: enabled)')
@click.option('--verbose', '-v', is_flag=True, help='Detailed output')
@click.option('--backup/--no-backup', default=True, help='Backup when fixing (default: enabled)')
def validate(file_path, language, fix, strict, verbose, backup):
    """Validate a Python or SQL file."""
    lang_enum = Language(language) if language else None
    
    validator = PythonSQLValidator(auto_fix=fix, strict_mode=strict)
    report = validator.validate_file(file_path)
    
    print_report(report, verbose)
    
    # Save fixes
    if fix and report.fixed_code and report.fixed_code != report.original_code:
        file_path = Path(file_path)
        
        if backup:
            # Create backup with -original suffix for better clarity
            backup_path = file_path.with_name(f"{file_path.stem}-original{file_path.suffix}")
            backup_path.write_text(report.original_code)
            click.echo(f"📄 Backup: {backup_path}")
        
        file_path.write_text(report.fixed_code)
        click.echo(f"💾 Fixed: {file_path}")


@cli.command()
@click.argument('pattern')
@click.option('--fix/--no-fix', default=True, help='Auto-fix all files (default: enabled)')
@click.option('--strict/--no-strict', default=True, help='Enable strict checks (default: enabled)')
def batch(pattern, fix, strict):
    """Batch validate files using glob pattern."""
    import glob
    
    files = glob.glob(pattern, recursive=True)
    if not files:
        click.echo(f"No files found: {pattern}")
        return
    
    validator = PythonSQLValidator(auto_fix=fix, strict_mode=strict)
    
    click.echo(f"Validating {len(files)} files...")
    
    valid_count = 0
    for filepath in files:
        report = validator.validate_file(filepath)
        status = "✅" if report.is_valid else "❌"
        click.echo(f"{status} {filepath}")
        
        if report.is_valid:
            valid_count += 1
        
        # Show critical issues
        errors = [i for i in report.issues if i.severity == "error"]
        if errors:
            for error in errors[:3]:  # Show first 3 errors
                click.echo(f"   ❌ Line {error.line_number}: {error.message}")
    
    click.echo(f"\nSummary: {valid_count}/{len(files)} files valid")


if __name__ == "__main__":
    cli()