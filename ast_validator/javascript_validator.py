#!/usr/bin/env python3
"""
JavaScript Code Validator
=========================

Focused validator for Front-end Developers.
Validates JavaScript, JSX, and modern ES6+ code with front-end specific
checks and auto-fixes.

Usage:
    python js_validator.py                      # Interactive mode
    python js_validator.py validate script.js   # Validate JavaScript
    python js_validator.py validate app.jsx     # Validate JSX
    python js_validator.py batch "src/**/*.js"  # Batch validate
    
Features:
- Node.js based syntax validation
- Modern JavaScript (ES6+) support
- JSX validation
- Auto-fix common issues (semicolons, quotes, formatting)
- Security checks for XSS and unsafe patterns
- Performance suggestions for React/frontend code
"""

import re
import json
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import click


class JSLanguage(Enum):
    JAVASCRIPT = "javascript"
    JSX = "jsx"
    TYPESCRIPT = "typescript"


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
    language: JSLanguage
    result: ValidationResult
    is_valid: bool
    issues: List[CodeIssue]
    original_code: str
    fixed_code: Optional[str] = None
    execution_safe: bool = False
    performance_score: Optional[int] = None


class JavaScriptValidator:
    """JavaScript/JSX validator for frontend developers"""
    
    def __init__(self, auto_fix: bool = True, strict_mode: bool = False):
        self.auto_fix = auto_fix
        self.strict_mode = strict_mode
        self.node_available = self._check_node_availability()
    
    def _check_node_availability(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def detect_language(self, code: str, filename: str = "") -> JSLanguage:
        """Detect JavaScript variant"""
        if filename:
            ext = Path(filename).suffix.lower()
            if ext == '.jsx':
                return JSLanguage.JSX
            elif ext in ['.ts', '.tsx']:
                return JSLanguage.TYPESCRIPT
        
        # JSX detection
        jsx_patterns = [
            r'<[A-Z][A-Za-z0-9]*[^>]*>',  # React components
            r'<[a-z]+[^>]*>.*</[a-z]+>',  # HTML elements
            r'className=',
            r'React\.createElement',
        ]
        
        if any(re.search(pattern, code) for pattern in jsx_patterns):
            return JSLanguage.JSX
        
        return JSLanguage.JAVASCRIPT
    
    def validate_code(self, code: str, language: Optional[JSLanguage] = None, filename: str = "") -> ValidationReport:
        """Validate JavaScript/JSX code"""
        if language is None:
            language = self.detect_language(code, filename)
        
        issues = []
        result = ValidationResult.VALID
        is_valid = True
        fixed_code = None
        
        try:
            # Node.js validation if available
            if self.node_available:
                is_valid, node_issues = self._validate_with_node(code, language)
                issues.extend(node_issues)
            else:
                # Fallback to basic validation
                is_valid = self._basic_js_validation(code)
                if not is_valid:
                    issues.append(CodeIssue(0, 0, "Basic syntax check failed", "SyntaxError"))
                
                issues.append(CodeIssue(0, 0, "Node.js not available - limited validation", 
                                      "MissingDependency", severity="warning"))
            
            if not is_valid:
                result = ValidationResult.SYNTAX_ERROR
                
                # Try auto-fixes
                if self.auto_fix:
                    fixed_code = self._fix_javascript_code(code, language)
                    if fixed_code != code:
                        if self.node_available:
                            fixed_valid, _ = self._validate_with_node(fixed_code, language)
                        else:
                            fixed_valid = self._basic_js_validation(fixed_code)
                        
                        if fixed_valid:
                            result = ValidationResult.FIXED
                            is_valid = True
                            issues.append(CodeIssue(0, 0, "Auto-fixed JavaScript", "AutoFix", severity="info"))
            
            # Frontend-specific checks
            if self.strict_mode and is_valid:
                issues.extend(self._frontend_checks(code, language))
            
            # Performance analysis
            performance_score = self._analyze_performance(code, language) if is_valid else None
            
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"Validation error: {str(e)}", "ValidationError"))
            is_valid = False
            result = ValidationResult.SYNTAX_ERROR
        
        return ValidationReport(
            language=language,
            result=result,
            is_valid=is_valid,
            issues=issues,
            original_code=code,
            fixed_code=fixed_code,
            execution_safe=self._check_security(code),
            performance_score=performance_score
        )
    
    def _validate_with_node(self, code: str, language: JSLanguage) -> Tuple[bool, List[CodeIssue]]:
        """Validate using Node.js"""
        issues = []
        
        try:
            # Create temp file with appropriate extension
            ext = '.jsx' if language == JSLanguage.JSX else '.js'
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                # For JSX, wrap in a basic React setup
                if language == JSLanguage.JSX:
                    wrapped_code = f"""
// React JSX validation wrapper
const React = {{ createElement: () => {{}} }};
{code}
"""
                    f.write(wrapped_code)
                else:
                    f.write(code)
                temp_file = f.name
            
            # Run Node.js syntax check
            result = subprocess.run(
                ['node', '--check', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            Path(temp_file).unlink()
            
            if result.returncode == 0:
                return True, issues
            else:
                # Parse Node.js errors
                for line in result.stderr.strip().split('\n'):
                    if 'SyntaxError' in line or 'Error' in line:
                        # Extract line number
                        line_match = re.search(r':(\d+):', line)
                        line_num = int(line_match.group(1)) if line_match else 0
                        
                        # Adjust line number for JSX wrapper
                        if language == JSLanguage.JSX and line_num > 2:
                            line_num -= 2
                        
                        issues.append(CodeIssue(
                            line_number=line_num,
                            column=0,
                            message=line.strip(),
                            error_type="SyntaxError"
                        ))
                
                return False, issues
                
        except Exception as e:
            issues.append(CodeIssue(0, 0, f"Node.js validation failed: {str(e)}", "ValidationError"))
            return self._basic_js_validation(code), issues
    
    def _basic_js_validation(self, code: str) -> bool:
        """Basic JavaScript validation without Node.js"""
        # Check balanced braces, brackets, parentheses
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        in_string = False
        in_comment = False
        escape_next = False
        string_char = None
        
        i = 0
        while i < len(code):
            char = code[i]
            
            if escape_next:
                escape_next = False
                i += 1
                continue
            
            if char == '\\' and in_string:
                escape_next = True
                i += 1
                continue
            
            # String handling
            if char in ['"', "'", '`'] and not in_comment:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                i += 1
                continue
            
            if in_string:
                i += 1
                continue
            
            # Comment handling
            if char == '/' and i + 1 < len(code):
                next_char = code[i + 1]
                if next_char == '/':
                    # Line comment
                    while i < len(code) and code[i] != '\n':
                        i += 1
                    continue
                elif next_char == '*':
                    # Block comment
                    i += 2
                    while i + 1 < len(code):
                        if code[i] == '*' and code[i + 1] == '/':
                            i += 2
                            break
                        i += 1
                    continue
            
            # Bracket matching
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return False
            
            i += 1
        
        return len(stack) == 0 and not in_string
    
    def _fix_javascript_code(self, code: str, language: JSLanguage) -> str:
        """Auto-fix JavaScript code issues"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Add missing semicolons
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ')', ',', ':', '//', '/*')):
                # Don't add semicolon to control structures or JSX
                if not any(stripped.startswith(keyword) for keyword in 
                          ['if', 'for', 'while', 'function', 'class', 'const', 'let', 'var', 'return', 'import', 'export']):
                    if not (language == JSLanguage.JSX and ('<' in stripped or '>' in stripped)):
                        line = line.rstrip() + ';'
            
            # Fix quote consistency (prefer single quotes)
            if '"' in line and "'" not in line:
                line = line.replace('"', "'")
            
            fixed_lines.append(line)
        
        result = '\n'.join(fixed_lines)
        
        # Fix common JSX issues
        if language == JSLanguage.JSX:
            result = self._fix_jsx_issues(result)
        
        return result
    
    def _fix_jsx_issues(self, code: str) -> str:
        """Fix common JSX issues"""
        # Fix className quotes
        code = re.sub(r"className=([a-zA-Z0-9\-_]+)", r"className='\1'", code)
        
        # Fix self-closing tags
        code = re.sub(r'<(img|br|hr|input|meta|link)([^>]*)>', r'<\1\2 />', code)
        
        return code
    
    def _frontend_checks(self, code: str, language: JSLanguage) -> List[CodeIssue]:
        """Frontend-specific validation checks"""
        issues = []
        
        # React/JSX specific checks
        if language == JSLanguage.JSX:
            issues.extend(self._react_checks(code))
        
        # General frontend checks
        issues.extend(self._performance_checks(code))
        issues.extend(self._security_checks(code))
        
        return issues
    
    def _react_checks(self, code: str) -> List[CodeIssue]:
        """React-specific validation"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for missing key prop in lists
            if 'map(' in line and '{' in line and 'key=' not in line:
                issues.append(CodeIssue(
                    line_number=i,
                    column=0,
                    message="Missing 'key' prop in mapped elements",
                    error_type="ReactWarning",
                    severity="warning",
                    suggested_fix="Add unique key prop: key={item.id}"
                ))
            
            # Check for inline functions in JSX (performance)
            if re.search(r'onClick=\{.*=>', line):
                issues.append(CodeIssue(
                    line_number=i,
                    column=0,
                    message="Inline function in JSX may cause unnecessary re-renders",
                    error_type="PerformanceWarning",
                    severity="warning",
                    suggested_fix="Define function outside render or use useCallback"
                ))
            
            # Check for direct DOM manipulation
            if 'document.getElementById' in line or 'document.querySelector' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    column=0,
                    message="Direct DOM manipulation in React - use refs instead",
                    error_type="ReactAntiPattern",
                    severity="warning",
                    suggested_fix="Use useRef() hook or React refs"
                ))
        
        return issues
    
    def _performance_checks(self, code: str) -> List[CodeIssue]:
        """Performance-related checks"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for inefficient DOM queries
            if line.count('document.querySelector') > 1:
                issues.append(CodeIssue(
                    line_number=i,
                    column=0,
                    message="Multiple DOM queries - consider caching selectors",
                    error_type="PerformanceWarning",
                    severity="warning",
                    suggested_fix="Cache DOM elements in variables"
                ))
            
            # Check for synchronous operations in loops
            if 'for(' in line or '.forEach(' in line:
                if 'await' in line or 'fetch(' in line:
                    issues.append(CodeIssue(
                        line_number=i,
                        column=0,
                        message="Synchronous operations in loops can block UI",
                        error_type="PerformanceWarning",
                        severity="warning",
                        suggested_fix="Use Promise.all() for concurrent operations"
                    ))
        
        return issues
    
    def _security_checks(self, code: str) -> List[CodeIssue]:
        """Security-related checks"""
        issues = []
        lines = code.split('\n')
        
        dangerous_patterns = [
            (r'\.innerHTML\s*=', "XSS risk with innerHTML"),
            (r'eval\s*\(', "eval() is dangerous"),
            (r'new Function\s*\(', "Function constructor is dangerous"),
            (r'document\.write\s*\(', "document.write can cause XSS"),
            (r'dangerouslySetInnerHTML', "Review dangerouslySetInnerHTML usage carefully"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in dangerous_patterns:
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        line_number=i,
                        column=0,
                        message=message,
                        error_type="SecurityWarning",
                        severity="warning"
                    ))
        
        return issues
    
    def _check_security(self, code: str) -> bool:
        """Overall security assessment"""
        dangerous_patterns = [
            r'eval\s*\(',
            r'new Function\s*\(',
            r'\.innerHTML\s*=.*\+',  # Concatenated innerHTML
            r'document\.write\s*\(',
        ]
        
        return not any(re.search(pattern, code, re.IGNORECASE) for pattern in dangerous_patterns)
    
    def _analyze_performance(self, code: str, language: JSLanguage) -> int:
        """Analyze code performance (0-100 score)"""
        score = 100
        
        # Deduct for performance issues
        if 'document.querySelector' in code:
            score -= code.count('document.querySelector') * 5
        
        if language == JSLanguage.JSX:
            # Deduct for inline functions
            score -= len(re.findall(r'onClick=\{.*=>', code)) * 10
            
            # Deduct for missing keys
            map_count = code.count('.map(')
            key_count = code.count('key=')
            if map_count > key_count:
                score -= (map_count - key_count) * 15
        
        # Deduct for sync operations in loops
        if re.search(r'for.*await|forEach.*await', code):
            score -= 20
        
        return max(0, min(100, score))
    
    def validate_file(self, filepath: Union[str, Path]) -> ValidationReport:
        """Validate a JavaScript file"""
        filepath = Path(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.validate_code(code, filename=str(filepath))
        except FileNotFoundError:
            return ValidationReport(
                language=JSLanguage.JAVASCRIPT,
                result=ValidationResult.SYNTAX_ERROR,
                is_valid=False,
                issues=[CodeIssue(0, 0, f"File not found: {filepath}", "FileNotFound")],
                original_code=""
            )
        except UnicodeDecodeError as e:
            return ValidationReport(
                language=JSLanguage.JAVASCRIPT,
                result=ValidationResult.SYNTAX_ERROR,
                is_valid=False,
                issues=[CodeIssue(0, 0, f"Encoding error: {e}", "EncodingError")],
                original_code=""
            )


def print_js_report(report: ValidationReport, verbose: bool = False):
    """Print JavaScript validation report"""
    click.echo()
    click.echo("="*60)
    click.echo(f"JAVASCRIPT VALIDATION ({report.language.value.upper()})")
    click.echo("="*60)
    
    status_icon = "✅" if report.is_valid else "❌"
    click.echo(f"Status: {status_icon} {report.result.value.upper()}")
    
    if report.execution_safe:
        click.echo("Security: 🟢 Safe")
    else:
        click.echo("Security: 🟡 Review needed")
    
    if report.performance_score is not None:
        score_icon = "🟢" if report.performance_score >= 80 else "🟡" if report.performance_score >= 60 else "🔴"
        click.echo(f"Performance: {score_icon} {report.performance_score}/100")
    
    if report.issues:
        click.echo(f"\nIssues ({len(report.issues)}):")
        click.echo("-" * 30)
        
        # Group issues by severity
        errors = [i for i in report.issues if i.severity == "error"]
        warnings = [i for i in report.issues if i.severity == "warning"]
        info = [i for i in report.issues if i.severity == "info"]
        
        for issue_list, severity in [(errors, "ERRORS"), (warnings, "WARNINGS"), (info, "INFO")]:
            if issue_list:
                click.echo(f"\n{severity}:")
                for issue in issue_list:
                    icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[issue.severity]
                    click.echo(f"  {icon} Line {issue.line_number}: {issue.message}")
                    if issue.suggested_fix:
                        click.echo(f"     💡 {issue.suggested_fix}")
    
    if report.fixed_code and verbose:
        click.echo(f"\nFixed Code:")
        click.echo("-" * 30)
        click.echo(report.fixed_code)


def interactive_mode():
    """Interactive JavaScript validation"""
    click.echo("🔍 JavaScript Code Validator")
    click.echo("Enter JavaScript/JSX code (type 'END' to finish, 'quit' to exit)")
    click.echo("-" * 60)
    
    validator = JavaScriptValidator(auto_fix=True, strict_mode=True)
    
    if not validator.node_available:
        click.echo("⚠️  Node.js not detected - using basic validation only")
        click.echo("   Install Node.js for full syntax checking")
    
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
            print_js_report(report, verbose=True)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """JavaScript code validator for Frontend Developers."""
    if ctx.invoked_subcommand is None:
        interactive_mode()


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--language', '-l', type=click.Choice(['javascript', 'jsx', 'typescript']), 
              help='Force language detection')
@click.option('--fix', is_flag=True, help='Auto-fix and save')
@click.option('--strict', is_flag=True, help='Enable React/performance checks')
@click.option('--verbose', '-v', is_flag=True, help='Detailed output')
@click.option('--backup/--no-backup', default=True, help='Backup when fixing')
def validate(file_path, language, fix, strict, verbose, backup):
    """Validate a JavaScript/JSX file."""
    lang_enum = JSLanguage(language) if language else None
    
    validator = JavaScriptValidator(auto_fix=fix, strict_mode=strict)
    report = validator.validate_file(file_path)
    
    print_js_report(report, verbose)
    
    # Save fixes
    if fix and report.fixed_code and report.fixed_code != report.original_code:
        file_path = Path(file_path)
        
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            backup_path.write_text(report.original_code)
            click.echo(f"📄 Backup: {backup_path}")
        
        file_path.write_text(report.fixed_code)
        click.echo(f"💾 Fixed: {file_path}")


@cli.command()
@click.argument('pattern')
@click.option('--fix', is_flag=True, help='Auto-fix all files')
@click.option('--strict', is_flag=True, help='Enable strict checks')
@click.option('--performance', is_flag=True, help='Show performance scores')
def batch(pattern, fix, strict, performance):
    """Batch validate JavaScript files using glob pattern."""
    import glob
    
    files = glob.glob(pattern, recursive=True)
    js_files = [f for f in files if Path(f).suffix in ['.js', '.jsx', '.mjs', '.ts', '.tsx']]
    
    if not js_files:
        click.echo(f"No JavaScript files found: {pattern}")
        return
    
    validator = JavaScriptValidator(auto_fix=fix, strict_mode=strict)
    
    click.echo(f"Validating {len(js_files)} JavaScript files...")
    
    valid_count = 0
    total_performance = 0
    
    for filepath in js_files:
        report = validator.validate_file(filepath)
        status = "✅" if report.is_valid else "❌"
        
        perf_info = ""
        if performance and report.performance_score is not None:
            perf_icon = "🟢" if report.performance_score >= 80 else "🟡" if report.performance_score >= 60 else "🔴"
            perf_info = f" {perf_icon} {report.performance_score}"
            total_performance += report.performance_score
        
        click.echo(f"{status} {filepath}{perf_info}")
        
        if report.is_valid:
            valid_count += 1
        
        # Show critical issues
        errors = [i for i in report.issues if i.severity == "error"]
        if errors:
            for error in errors[:2]:  # Show first 2 errors
                click.echo(f"   ❌ Line {error.line_number}: {error.message}")
        
        # Show security warnings
        security_issues = [i for i in report.issues if "Security" in i.error_type]
        if security_issues:
            for issue in security_issues[:1]:
                click.echo(f"   🔒 Line {issue.line_number}: {issue.message}")
    
    click.echo(f"\nSummary: {valid_count}/{len(js_files)} files valid")
    
    if performance and js_files:
        avg_performance = total_performance / len(js_files)
        click.echo(f"Average Performance Score: {avg_performance:.1f}/100")


@cli.command()
def setup():
    """Check setup and dependencies."""
    click.echo("JavaScript Validator Setup Check")
    click.echo("=" * 35)
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ Node.js: {result.stdout.strip()}")
        else:
            click.echo("❌ Node.js: Not working properly")
    except FileNotFoundError:
        click.echo("❌ Node.js: Not installed")
        click.echo("   Install from: https://nodejs.org/")
    
    # Check npm (optional)
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        click.echo("⚠️  npm: Not available (optional)")
    
    click.echo("\nRecommended for enhanced validation:")
    click.echo("• ESLint: npm install -g eslint")
    click.echo("• Prettier: npm install -g prettier")
    click.echo("• TypeScript: npm install -g typescript")


if __name__ == "__main__":
    cli()