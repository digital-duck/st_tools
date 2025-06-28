#!/usr/bin/env python3
"""
Full-Stack Code Validator
=========================

Comprehensive validator for Full-Stack Engineers.
Supports Python, SQL, JavaScript, JSX, TypeScript, JSON, and more.
Combines all validation capabilities with project-level analysis.

Usage:
    python fullstack_validator.py                    # Interactive mode
    python fullstack_validator.py validate file.py   # Single file
    python fullstack_validator.py project ./myapp    # Whole project
    python fullstack_validator.py batch "**/*.{py,js,sql}" # Multi-language batch
    
Features:
- Multi-language validation in one tool
- Project-wide analysis and reporting
- Cross-language dependency checking
- Architecture recommendations
- CI/CD integration ready
"""

import ast
import re
import json
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

import click


class Language(Enum):
    PYTHON = "python"
    SQL = "sql"
    JAVASCRIPT = "javascript"
    JSX = "jsx"
    TYPESCRIPT = "typescript"
    JSON = "json"
    YAML = "yaml"
    HTML = "html"
    CSS = "css"


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
    file_path: str = ""
    suggested_fix: Optional[str] = None
    severity: str = "error"  # error, warning, info


@dataclass
class FileReport:
    filepath: str
    language: Language
    result: ValidationResult
    is_valid: bool
    issues: List[CodeIssue] = field(default_factory=list)
    original_code: str = ""
    fixed_code: Optional[str] = None
    execution_safe: bool = False
    performance_score: Optional[int] = None
    complexity_score: Optional[int] = None


@dataclass
class ProjectReport:
    project_path: str
    total_files: int
    valid_files: int
    languages_found: Set[Language] = field(default_factory=set)
    file_reports: List[FileReport] = field(default_factory=list)
    architecture_issues: List[CodeIssue] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class FullStackValidator:
    """Comprehensive multi-language validator"""
    
    def __init__(self, auto_fix: bool = True, strict_mode: bool = False):
        self.auto_fix = auto_fix
        self.strict_mode = strict_mode
        self.node_available = self._check_node()
        self.supported_extensions = {
            '.py': Language.PYTHON,
            '.sql': Language.SQL,
            '.js': Language.JAVASCRIPT,
            '.mjs': Language.JAVASCRIPT,
            '.jsx': Language.JSX,
            '.ts': Language.TYPESCRIPT,
            '.tsx': Language.TYPESCRIPT,
            '.json': Language.JSON,
            '.yaml': Language.YAML,
            '.yml': Language.YAML,
            '.html': Language.HTML,
            '.htm': Language.HTML,
            '.css': Language.CSS,
        }
    
    def _check_node(self) -> bool:
        """Check Node.js availability"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def detect_language(self, code: str, filename: str = "") -> Language:
        """Smart language detection"""
        if filename:
            ext = Path(filename).suffix.lower()
            if ext in self.supported_extensions:
                return self.supported_extensions[ext]
        
        # Content-based detection
        code_strip = code.strip()
        
        # JSON detection
        if (code_strip.startswith(('{', '[')) and code_strip.endswith(('}', ']'))):
            try:
                json.loads(code)
                return Language.JSON
            except:
                pass
        
        # YAML detection
        if re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:\s*', code, re.MULTILINE):
            return Language.YAML
        
        # SQL detection
        if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b', code, re.IGNORECASE):
            return Language.SQL
        
        # JSX detection
        if re.search(r'<[A-Z][A-Za-z0-9]*|className=|React\.', code):
            return Language.JSX
        
        # JavaScript detection
        if re.search(r'\b(function|const|let|var|=>|console\.log)\b', code):
            return Language.JAVASCRIPT
        
        # HTML detection
        if re.search(r'<!DOCTYPE|<html|<head|<body', code, re.IGNORECASE):
            return Language.HTML
        
        # CSS detection
        if re.search(r'[a-zA-Z-]+\s*:\s*[^;]+;|\{[^}]*\}', code):
            return Language.CSS
        
        return Language.PYTHON  # Default fallback
    
    def validate_file(self, filepath: Union[str, Path]) -> FileReport:
        """Validate a single file"""
        filepath = Path(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return FileReport(
                filepath=str(filepath),
                language=Language.PYTHON,
                result=ValidationResult.SYNTAX_ERROR,
                is_valid=False,
                issues=[CodeIssue(0, 0, f"Read error: {e}", "FileError", str(filepath))]
            )
        
        language = self.detect_language(code, str(filepath))
        
        # Validate based on language
        if language == Language.PYTHON:
            return self._validate_python_file(filepath, code)
        elif language == Language.SQL:
            return self._validate_sql_file(filepath, code)
        elif language in [Language.JAVASCRIPT, Language.JSX, Language.TYPESCRIPT]:
            return self._validate_js_file(filepath, code, language)
        elif language == Language.JSON:
            return self._validate_json_file(filepath, code)
        elif language == Language.YAML:
            return self._validate_yaml_file(filepath, code)
        else:
            return FileReport(
                filepath=str(filepath),
                language=language,
                result=ValidationResult.VALID,
                is_valid=True,
                issues=[CodeIssue(0, 0, f"Basic validation for {language.value}", "Info", str(filepath), severity="info")]
            )
    
    def _validate_python_file(self, filepath: Path, code: str) -> FileReport:
        """Validate Python file"""
        issues = []
        fixed_code = None
        ast_tree = None
        result = ValidationResult.SYNTAX_ERROR
        
        try:
            ast_tree = ast.parse(code, filename=str(filepath))
            result = ValidationResult.VALID
            is_valid = True
            
            # Add file path to issues
            if self.strict_mode:
                issues.extend(self._python_advanced_checks(ast_tree, code, str(filepath)))
                
        except SyntaxError as e:
            issues.append(CodeIssue(
                line_number=e.lineno or 0,
                column=e.offset or 0,
                message=f"Syntax Error: {e.msg}",
                error_type="SyntaxError",
                file_path=str(filepath)
            ))
            
            if self.auto_fix:
                fixed_code = self._fix_python_code(code)
                if fixed_code != code:
                    try:
                        ast.parse(fixed_code)
                        result = ValidationResult.FIXED
                        is_valid = True
                        issues.append(CodeIssue(0, 0, "Auto-fixed", "AutoFix", str(filepath), severity="info"))
                    except:
                        is_valid = False
                else:
                    is_valid = False
            else:
                is_valid = False
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"Parse error: {e}", "ParseError", str(filepath)))
            is_valid = False
        
        return FileReport(
            filepath=str(filepath),
            language=Language.PYTHON,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=self._check_python_safety(code),
            complexity_score=self._calculate_complexity(code, Language.PYTHON)
        )
    
    def _validate_sql_file(self, filepath: Path, code: str) -> FileReport:
        """Validate SQL file"""
        issues = []
        fixed_code = None
        result = ValidationResult.VALID
        is_valid = True
        
        try:
            import sqlparse
            parsed = sqlparse.parse(code)
            
            if self.auto_fix:
                formatted = sqlparse.format(code, reindent=True, keyword_case='upper')
                if formatted != code:
                    fixed_code = formatted
                    result = ValidationResult.FIXED
                    issues.append(CodeIssue(0, 0, "SQL formatted", "AutoFormat", str(filepath), severity="info"))
            
        except ImportError:
            issues.append(CodeIssue(0, 0, "sqlparse not available", "MissingDependency", str(filepath), severity="warning"))
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"SQL error: {e}", "SQLError", str(filepath)))
            is_valid = False
            result = ValidationResult.SYNTAX_ERROR
        
        return FileReport(
            filepath=str(filepath),
            language=Language.SQL,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=True
        )
    
    def _validate_js_file(self, filepath: Path, code: str, language: Language) -> FileReport:
        """Validate JavaScript/JSX/TypeScript file"""
        issues = []
        fixed_code = None
        result = ValidationResult.VALID
        is_valid = True
        
        if self.node_available:
            is_valid, node_issues = self._validate_js_with_node(code, language)
            issues.extend([CodeIssue(i.line_number, i.column, i.message, i.error_type, str(filepath)) for i in node_issues])
        else:
            issues.append(CodeIssue(0, 0, "Node.js not available", "MissingDependency", str(filepath), severity="warning"))
            is_valid = self._basic_js_validation(code)
        
        if not is_valid:
            result = ValidationResult.SYNTAX_ERROR
        
        if self.auto_fix and result == ValidationResult.SYNTAX_ERROR:
            fixed_code = self._fix_js_code(code, language)
            if fixed_code != code:
                result = ValidationResult.FIXED
                is_valid = True
                issues.append(CodeIssue(0, 0, "Auto-fixed JS", "AutoFix", str(filepath), severity="info"))
        
        return FileReport(
            filepath=str(filepath),
            language=language,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=self._check_js_safety(code),
            performance_score=self._calculate_js_performance(code, language)
        )
    
    def _validate_json_file(self, filepath: Path, code: str) -> FileReport:
        """Validate JSON file"""
        issues = []
        fixed_code = None
        result = ValidationResult.VALID
        is_valid = True
        
        try:
            json_obj = json.loads(code)
            
            if self.auto_fix:
                formatted = json.dumps(json_obj, indent=2, ensure_ascii=False)
                if formatted != code.strip():
                    fixed_code = formatted
                    result = ValidationResult.FIXED
                    issues.append(CodeIssue(0, 0, "JSON formatted", "AutoFormat", str(filepath), severity="info"))
                    
        except json.JSONDecodeError as e:
            issues.append(CodeIssue(
                line_number=e.lineno,
                column=e.colno,
                message=f"JSON Error: {e.msg}",
                error_type="JSONError",
                file_path=str(filepath)
            ))
            is_valid = False
            result = ValidationResult.SYNTAX_ERROR
        
        return FileReport(
            filepath=str(filepath),
            language=Language.JSON,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=True
        )
    
    def _validate_yaml_file(self, filepath: Path, code: str) -> FileReport:
        """Validate YAML file"""
        issues = []
        result = ValidationResult.VALID
        is_valid = True
        
        try:
            import yaml
            yaml.safe_load(code)
        except ImportError:
            issues.append(CodeIssue(0, 0, "PyYAML not available", "MissingDependency", str(filepath), severity="warning"))
        except yaml.YAMLError as e:
            issues.append(CodeIssue(0, 0, f"YAML Error: {e}", "YAMLError", str(filepath)))
            is_valid = False
            result = ValidationResult.SYNTAX_ERROR
        
        return FileReport(
            filepath=str(filepath),
            language=Language.YAML,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            execution_safe=True
        )
    
    def validate_project(self, project_path: Union[str, Path]) -> ProjectReport:
        """Validate entire project"""
        project_path = Path(project_path)
        
        # Find all code files
        code_files = []
        for ext in self.supported_extensions:
            code_files.extend(project_path.rglob(f"*{ext}"))
        
        # Filter out common ignore patterns
        ignore_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'dist', 'build', '.next'
        }
        
        code_files = [f for f in code_files if not any(part in ignore_patterns for part in f.parts)]
        
        # Validate each file
        file_reports = []
        languages_found = set()
        
        with click.progressbar(code_files, label='Validating files') as files:
            for filepath in files:
                report = self.validate_file(filepath)
                file_reports.append(report)
                languages_found.add(report.language)
        
        # Analyze project architecture
        architecture_issues = self._analyze_project_architecture(project_path, file_reports)
        dependencies = self._analyze_dependencies(file_reports)
        recommendations = self._generate_recommendations(file_reports, languages_found)
        
        valid_files = sum(1 for r in file_reports if r.is_valid)
        
        return ProjectReport(
            project_path=str(project_path),
            total_files=len(file_reports),
            valid_files=valid_files,
            languages_found=languages_found,
            file_reports=file_reports,
            architecture_issues=architecture_issues,
            dependencies=dependencies,
            recommendations=recommendations
        )
    
    def _python_advanced_checks(self, ast_tree: ast.AST, code: str, filepath: str) -> List[CodeIssue]:
        """Advanced Python checks"""
        issues = []
        
        class AdvancedVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.complexity = 0
            
            def visit_FunctionDef(self, node):
                # Check function complexity
                if len(node.body) > 20:
                    self.issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' is too long ({len(node.body)} statements)",
                        error_type="ComplexityWarning",
                        file_path=filepath,
                        severity="warning",
                        suggested_fix="Consider breaking into smaller functions"
                    ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for problematic imports
                for alias in node.names:
                    if alias.name in ['os', 'subprocess'] and 'test' not in filepath.lower():
                        self.issues.append(CodeIssue(
                            line_number=node.lineno,
                            column=node.col_offset,
                            message=f"Potentially unsafe import: {alias.name}",
                            error_type="SecurityWarning",
                            file_path=filepath,
                            severity="warning"
                        ))
                self.generic_visit(node)
        
        visitor = AdvancedVisitor()
        visitor.visit(ast_tree)
        return visitor.issues
    
    def _analyze_project_architecture(self, project_path: Path, file_reports: List[FileReport]) -> List[CodeIssue]:
        """Analyze project architecture"""
        issues = []
        
        # Check for common architecture patterns
        python_files = [r for r in file_reports if r.language == Language.PYTHON]
        js_files = [r for r in file_reports if r.language in [Language.JAVASCRIPT, Language.JSX]]
        
        # Check for missing important files
        important_files = ['README.md', 'requirements.txt', 'package.json', '.gitignore']
        for filename in important_files:
            if not (project_path / filename).exists():
                issues.append(CodeIssue(
                    line_number=0,
                    column=0,
                    message=f"Missing {filename}",
                    error_type="ArchitectureWarning",
                    file_path=str(project_path),
                    severity="warning"
                ))
        
        # Check for mixed language projects without proper structure
        if len(python_files) > 0 and len(js_files) > 0:
            # Full-stack project
            if not (project_path / 'frontend').exists() and not (project_path / 'backend').exists():
                issues.append(CodeIssue(
                    line_number=0,
                    column=0,
                    message="Full-stack project should have clear frontend/backend separation",
                    error_type="ArchitectureRecommendation",
                    file_path=str(project_path),
                    severity="info",
                    suggested_fix="Consider organizing into frontend/ and backend/ directories"
                ))
        
        return issues
    
    def _analyze_dependencies(self, file_reports: List[FileReport]) -> Dict[str, List[str]]:
        """Analyze cross-file dependencies"""
        dependencies = defaultdict(list)
        
        for report in file_reports:
            if report.language == Language.PYTHON:
                # Extract Python imports
                try:
                    tree = ast.parse(report.original_code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                dependencies[report.filepath].append(alias.name)
                except:
                    pass
            
            elif report.language in [Language.JAVASCRIPT, Language.JSX]:
                # Extract JS imports
                import_pattern = r'import.*from\s+[\'"]([^\'"]+)[\'"]'
                imports = re.findall(import_pattern, report.original_code)
                dependencies[report.filepath].extend(imports)
        
        return dict(dependencies)
    
    def _generate_recommendations(self, file_reports: List[FileReport], languages: Set[Language]) -> List[str]:
        """Generate project recommendations"""
        recommendations = []
        
        # Language-specific recommendations
        if Language.PYTHON in languages:
            python_files = [r for r in file_reports if r.language == Language.PYTHON]
            if len(python_files) > 5:
                recommendations.append("Consider adding type hints for better code maintainability")
                recommendations.append("Set up pre-commit hooks with black and flake8")
        
        if Language.JAVASCRIPT in languages or Language.JSX in languages:
            recommendations.append("Consider adding ESLint and Prettier for code consistency")
            
        if Language.JSX in languages:
            recommendations.append("Consider adding PropTypes or TypeScript for type safety")
        
        # Multi-language recommendations
        if len(languages) > 2:
            recommendations.append("Consider containerization with Docker for consistent environments")
            recommendations.append("Set up CI/CD pipeline for multi-language validation")
        
        return recommendations
    
    # Helper methods for validation
    def _fix_python_code(self, code: str) -> str:
        """Basic Python fixes"""
        # Fix nested quotes
        code = re.sub(r"'''(.*?)'''", lambda m: f"'''{m.group(1).replace('\"\"\"', \"'''\")}'''", code, flags=re.DOTALL)
        return code
    
    def _fix_js_code(self, code: str, language: Language) -> str:
        """Basic JavaScript fixes"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Add missing semicolons
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ')', ',')):
                if not any(stripped.startswith(kw) for kw in ['if', 'for', 'while', 'function']):
                    line = line.rstrip() + ';'
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _basic_js_validation(self, code: str) -> bool:
        """Basic JS validation without Node.js"""
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        in_string = False
        string_char = None
        
        for char in code:
            if char in ['"', "'", '`'] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char in brackets:
                    stack.append(brackets[char])
                elif char in brackets.values():
                    if not stack or stack.pop() != char:
                        return False
        
        return len(stack) == 0 and not in_string
    
    def _validate_js_with_node(self, code: str, language: Language) -> Tuple[bool, List[CodeIssue]]:
        """Validate JS with Node.js"""
        issues = []
        try:
            ext = '.jsx' if language == Language.JSX else '.js'
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(['node', '--check', temp_file], capture_output=True, text=True, timeout=10)
            Path(temp_file).unlink()
            
            if result.returncode == 0:
                return True, issues
            else:
                for line in result.stderr.strip().split('\n'):
                    if 'Error' in line:
                        line_match = re.search(r':(\d+):', line)
                        line_num = int(line_match.group(1)) if line_match else 0
                        issues.append(CodeIssue(line_num, 0, line.strip(), "SyntaxError"))
                return False, issues
        except:
            return self._basic_js_validation(code), issues
    
    def _check_python_safety(self, code: str) -> bool:
        """Check Python safety"""
        dangerous = [r'\beval\s*\(', r'\bexec\s*\(', r'\bos\.system\s*\(']
        return not any(re.search(pattern, code, re.IGNORECASE) for pattern in dangerous)
    
    def _check_js_safety(self, code: str) -> bool:
        """Check JavaScript safety"""
        dangerous = [r'\beval\s*\(', r'\.innerHTML\s*=', r'document\.write\s*\(']
        return not any(re.search(pattern, code, re.IGNORECASE) for pattern in dangerous)
    
    def _calculate_complexity(self, code: str, language: Language) -> int:
        """Calculate code complexity score"""
        if language == Language.PYTHON:
            try:
                tree = ast.parse(code)
                complexity = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)))
                return min(100, max(0, 100 - complexity * 2))
            except:
                return 50
        return 50  # Default score
    
    def _calculate_js_performance(self, code: str, language: Language) -> int:
        """Calculate JS performance score"""
        score = 100
        if 'document.querySelector' in code:
            score -= code.count('document.querySelector') * 5
        if language == Language.JSX and '.map(' in code and 'key=' not in code:
            score -= 20
        return max(0, score)


def print_file_report(report: FileReport, verbose: bool = False):
    """Print single file report"""
    status_icon = "✅" if report.is_valid else "❌"
    lang_badge = f"[{report.language.value.upper()}]"
    
    click.echo(f"{status_icon} {lang_badge} {report.filepath}")
    
    if report.performance_score:
        perf_icon = "🟢" if report.performance_score >= 80 else "🟡" if report.performance_score >= 60 else "🔴"
        click.echo(f"   Performance: {perf_icon} {report.performance_score}/100")
    
    if report.issues and verbose:
        for issue in report.issues[:3]:  # Show first 3 issues
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[issue.severity]
            click.echo(f"   {icon} Line {issue.line_number}: {issue.message}")


def print_project_report(report: ProjectReport, verbose: bool = False):
    """Print comprehensive project report"""
    click.echo()
    click.echo("="*80)
    click.echo(f"FULL-STACK PROJECT VALIDATION REPORT")
    click.echo("="*80)
    
    # Summary
    success_rate = (report.valid_files / report.total_files * 100) if report.total_files > 0 else 0
    click.echo(f"Project: {report.project_path}")
    click.echo(f"Files: {report.valid_files}/{report.total_files} valid ({success_rate:.1f}%)")
    click.echo(f"Languages: {', '.join(lang.value for lang in sorted(report.languages_found, key=lambda x: x.value))}")
    
    # Language breakdown
    click.echo(f"\nLanguage Breakdown:")
    lang_counts = Counter(r.language for r in report.file_reports)
    for lang, count in lang_counts.most_common():
        valid_count = sum(1 for r in report.file_reports if r.language == lang and r.is_valid)
        click.echo(f"  {lang.value}: {valid_count}/{count} valid")
    
    # Architecture issues
    if report.architecture_issues:
        click.echo(f"\nArchitecture Issues:")
        for issue in report.architecture_issues:
            icon = {"warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "❓")
            click.echo(f"  {icon} {issue.message}")
    
    # Recommendations
    if report.recommendations:
        click.echo(f"\nRecommendations:")
        for rec in report.recommendations:
            click.echo(f"  💡 {rec}")
    
    # File details
    if verbose:
        click.echo(f"\nFile Details:")
        for report_file in report.file_reports:
            print_file_report(report_file, verbose=False)


def interactive_mode():
    """Interactive full-stack validation"""
    click.echo("🔍 Full-Stack Code Validator")
    click.echo("Supports: Python, SQL, JavaScript, JSX, TypeScript, JSON, YAML")
    click.echo("Enter code (type 'END' to finish, 'quit' to exit)")
    click.echo("-" * 70)
    
    validator = FullStackValidator(auto_fix=True, strict_mode=True)
    
    while True:
        click.echo("\nEnter code (or specify language with 'lang:python', etc):")
        lines = []
        specified_lang = None
        
        while True:
            line = input(">>> " if not lines else "... ")
            
            if line.strip() == 'END':
                break
            if line.strip() == 'quit':
                return
            
            # Check for language specification
            if line.startswith('lang:') and not lines:
                try:
                    specified_lang = Language(line.split(':', 1)[1].strip())
                    continue
                except ValueError:
                    click.echo(f"Unknown language: {line.split(':', 1)[1]}")
                    continue
            
            lines.append(line)
        
        if lines:
            code = '\n'.join(lines)
            
            # Create a temporary file report
            detected_lang = specified_lang or validator.detect_language(code)
            
            if detected_lang == Language.PYTHON:
                report = validator._validate_python_file(Path("<input>"), code)
            elif detected_lang == Language.SQL:
                report = validator._validate_sql_file(Path("<input>"), code)
            elif detected_lang in [Language.JAVASCRIPT, Language.JSX, Language.TYPESCRIPT]:
                report = validator._validate_js_file(Path("<input>"), code, detected_lang)
            elif detected_lang == Language.JSON:
                report = validator._validate_json_file(Path("<input>"), code)
            else:
                click.echo(f"Basic validation for {detected_lang.value}")
                continue
            
            print_file_report(report, verbose=True)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Full-Stack code validator for comprehensive project analysis."""
    if ctx.invoked_subcommand is None:
        interactive_mode()


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--language', '-l', type=click.Choice([lang.value for lang in Language]), 
              help='Force language detection')
@click.option('--fix', is_flag=True, help='Auto-fix and save')
@click.option('--strict', is_flag=True, help='Enable strict validation')
@click.option('--verbose', '-v', is_flag=True, help='Detailed output')
def validate(file_path, language, fix, strict, verbose):
    """Validate a single file."""
    validator = FullStackValidator(auto_fix=fix, strict_mode=strict)
    report = validator.validate_file(file_path)
    
    print_file_report(report, verbose)
    
    if fix and report.fixed_code and report.fixed_code != report.original_code:
        Path(file_path).write_text(report.fixed_code)
        click.echo(f"💾 Fixed: {file_path}")


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--fix', is_flag=True, help='Auto-fix all files')
@click.option('--strict', is_flag=True, help='Enable strict validation')
@click.option('--verbose', '-v', is_flag=True, help='Detailed file reports')
@click.option('--report', type=click.Path(), help='Save report to file')
def project(project_path, fix, strict, verbose, report):
    """Validate entire project."""
    validator = FullStackValidator(auto_fix=fix, strict_mode=strict)
    project_report = validator.validate_project(project_path)
    
    print_project_report(project_report, verbose)
    
    if report:
        # Save detailed report
        report_data = {
            'summary': {
                'total_files': project_report.total_files,
                'valid_files': project_report.valid_files,
                'languages': [lang.value for lang in project_report.languages_found]
            },
            'files': [
                {
                    'path': fr.filepath,
                    'language': fr.language.value,
                    'valid': fr.is_valid,
                    'issues': len(fr.issues)
                } for fr in project_report.file_reports
            ],
            'recommendations': project_report.recommendations
        }
        
        with open(report, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        click.echo(f"\n📄 Report saved to: {report}")


@cli.command()
@click.argument('pattern')
@click.option('--fix', is_flag=True, help='Auto-fix all files')
@click.option('--strict', is_flag=True, help='Enable strict validation')
def batch(pattern, fix, strict):
    """Batch validate files using glob pattern."""
    import glob
    
    files = glob.glob(pattern, recursive=True)
    if not files:
        click.echo(f"No files found: {pattern}")
        return
    
    validator = FullStackValidator(auto_fix=fix, strict_mode=strict)
    
    click.echo(f"Validating {len(files)} files...")
    
    lang_stats = defaultdict(lambda: {'total': 0, 'valid': 0})
    
    for filepath in files:
        report = validator.validate_file(filepath)
        status = "✅" if report.is_valid else "❌"
        click.echo(f"{status} [{report.language.value.upper()}] {filepath}")
        
        lang_stats[report.language]['total'] += 1
        if report.is_valid:
            lang_stats[report.language]['valid'] += 1
    
    # Summary
    click.echo(f"\nSummary by Language:")
    for lang, stats in lang_stats.items():
        success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
        click.echo(f"  {lang.value}: {stats['valid']}/{stats['total']} ({success_rate:.1f}%)")


if __name__ == "__main__":
    cli()