import re

KNOWN_LANGUAGES = ['mermaid', 'python', 'sql', 'javascript', 'js', 'html', 'css', 'json', 'yaml', 'markdown', 'md']
KNOWN_MERMAID_TYPES = ['flowchart', 'sequenceDiagram', 'stateDiagram', 'gantt', 'journey', 'gitgraph']
KNOWN_XML_TAGS = ["reasoning", "analysis", "thinking"]

def strip_specific_language_tags(code: str, languages: list = None) -> str:
    """Remove markdown tags for specific programming languages."""
    if not code:
        return ""
    
    if languages is None:
        languages = KNOWN_LANGUAGES
    
    # Create pattern for specified languages - handle case where only one language is provided
    if len(languages) == 1:
        lang = languages[0]
        # Remove opening tag for this specific language only
        code = re.sub(rf'```{re.escape(lang)}\n?', '', code, flags=re.IGNORECASE)
    else:
        # Remove opening tags for any of the specified languages
        lang_pattern = '|'.join(re.escape(lang) for lang in languages)
        code = re.sub(rf'```(?:{lang_pattern})\n?', '', code, flags=re.IGNORECASE)
    
    # Remove closing tags
    code = re.sub(r'```\n?', '', code)
    
    # For unknown content detected as specific type, apply additional cleaning
    first_lang = languages[0] if languages else ""
    if first_lang == 'sql':
        # Remove "Here's the SQL:" type prefixes specifically
        code = re.sub(r'^.*?SQL:\s*\n?', '', code, flags=re.IGNORECASE | re.MULTILINE)
    elif first_lang == 'javascript':
        # Handle HTML pre/code tags
        code = re.sub(r'</?(?:pre|code)[^>]*>', '', code, flags=re.IGNORECASE)
    elif first_lang == 'python':
        # Remove explanatory text around python code
        code = re.sub(r'^.*?code:\s*\n?', '', code, flags=re.IGNORECASE | re.MULTILINE)
        code = re.sub(r'\n+The result is.*\n?', '', code, flags=re.IGNORECASE | re.MULTILINE)

    return code.strip()

def _extract_tag_content(text: str, tag: str) -> str:
    """Extract content from XML-style tags."""
    pattern = rf'<{tag}>(.*?)</{tag}>'
    matches = re.findall(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return '\n'.join(matches).strip() if matches else ""


def _detect_content_type(text: str) -> str:
    """Detect the primary content type in the text."""
    # Check for code fences first (highest priority)
    fence_match = re.search(r'```(\w+)', text, re.IGNORECASE)
    if fence_match:
        lang = fence_match.group(1).lower()
        if lang in KNOWN_LANGUAGES:
            return lang
    
    # Check for Mermaid keywords (before other patterns)
    for keyword in KNOWN_MERMAID_TYPES:
        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            return 'mermaid'
    
    # Check for programming language patterns
    if re.search(r'\bdef\s+\w+\s*\(|import\s+\w+|from\s+\w+\s+import|\bprint\s*\(', text):
        return 'python'
    if re.search(r'\bfunction\s+\w+\s*\(|const\s+\w+\s*=|console\.log|let\s+\w+', text):
        return 'javascript'
    if re.search(r'<html|<head>|<body>|<!DOCTYPE', text, re.IGNORECASE):
        return 'html'
    if re.search(r'\bSELECT\s+.*\bFROM\b|\bINSERT\s+INTO\b|\bUPDATE\s+.*\bSET\b', text, re.IGNORECASE):
        return 'sql'
    
    return "unknown"


def _clean_mermaid_specific(code: str) -> str:
    """Additional cleaning specific to Mermaid diagrams."""
    # Remove any remaining thinking tags that might have been missed
    code = re.sub(r'</thinking>\n?', '', code, flags=re.IGNORECASE)
    
    # Remove explanatory text before mermaid keywords
    for keyword in KNOWN_MERMAID_TYPES:
        # Find the keyword and extract from there to end (or until double newline)
        pattern = rf'^.*?({re.escape(keyword)}.*?)(?:\n\n.*?$|$)'
        match = re.search(pattern, code, flags=re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # If no keyword match, try to find and remove extra text before flowchart
    # Handle case where there's leftover text like "flowchart" before the actual diagram
    lines = code.split('\n')
    cleaned_lines = []
    found_start = False
    
    for line in lines:
        # Skip standalone "flowchart" lines without proper syntax
        if line.strip() == 'flowchart' and not found_start:
            continue
        # Look for proper mermaid diagram start
        if any(line.strip().startswith(keyword) for keyword in KNOWN_MERMAID_TYPES):
            found_start = True
        if found_start:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip() if cleaned_lines else code.strip()


def _basic_clean(text: str, preserve_comments: bool) -> str:
    """Basic cleaning for unknown content types."""
    # Remove thinking tags
    for tag in KNOWN_XML_TAGS:
        text = re.sub(rf'<{tag}>.*?</{tag}>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(rf'</?{tag}>', '', text, flags=re.IGNORECASE)
    
    # Remove all code fences
    text = re.sub(r'```\w*\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\n?', '', text)
    
    # Remove HTML tags
    text = re.sub(r'</?(?:pre|code)[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Remove common LLM explanations at start
    text = re.sub(r'^(Here\'s|Here is|This is).*?:\s*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove trailing explanations 
    text = re.sub(r'\n\n+(The result is|This does|Explanation:).*\n?', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text.strip()


def _remove_comments(code: str) -> str:
    """Remove code comments."""
    # Python/shell comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    # JavaScript/C++ comments
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    # C-style block comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # HTML comments
    code = re.sub(r'<!--.*?-->', '', code, flags=re.DOTALL)
    
    return code.strip()


def _final_cleanup(code: str) -> str:
    """Final cleanup of extracted code."""
    if not code:
        return ""
    
    # Remove extra whitespace and empty lines
    lines = [line.rstrip() for line in code.split('\n')]
    
    # Remove leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(lines)

def clean_llm_output(llm_output: str, preserve_comments: bool = True) -> dict:
    """
    Comprehensive cleaner for different types of LLM output with auto-detection.
    
    Args:
        llm_output (str): Raw LLM output
        preserve_comments (bool): Whether to preserve code comments
        
    Returns:
        dict: {
            "code": "cleaned code content",
            "reasoning": "extracted reasoning text",
            "analysis": "extracted analysis text", 
            "thinking": "extracted thinking text",
            "error": "error message if any",
            "content_type": "detected content type"
        }
    """
    if not llm_output:
        return {"error": "Empty input"}
    
    result = {"code": "", "error": ""}
    
    # Extract tagged content
    for tag in KNOWN_XML_TAGS:
        result[tag] = _extract_tag_content(llm_output, tag)
    
    # Detect content type and clean accordingly
    detected_type = _detect_content_type(llm_output)
    result["content_type"] = detected_type
    
    if detected_type in KNOWN_LANGUAGES:
        # Known content type - use specific processing
        result["code"] = strip_specific_language_tags(llm_output, [detected_type])
        
        # Additional cleaning for specific types
        if detected_type == 'mermaid':
            result["code"] = _clean_mermaid_specific(result["code"])
    else:
        # Unknown content type - warning and default processing
        print("⚠️  Warning: Failed to detect content type - applying default processing")
        result["code"] = _basic_clean(llm_output, preserve_comments)
    
    # Remove comments if not preserving them
    if not preserve_comments:
        result["code"] = _remove_comments(result["code"])
    
    # Clean up the final code
    result["code"] = _final_cleanup(result["code"])
    
    return result


# Test cases
if __name__ == "__main__":
    test_cases = [
        '''<thinking>Need to create a workflow</thinking>
```mermaid
flowchart TD
    A --> B
```''',
        
        # Python code with markdown
        '```python\nprint("hello world")\n```',
        
        '''Here's the SQL:
```sql
select count(*) from t_customers;
```
''',
        
        # Multiple code blocks
        '''```python
def hello():
    return "world"
```

```javascript
console.log("hello");
```''',

        # Javascript code blocks
        '''
```javascript
console.log("hello");
```''',
        
        # With thinking tags
        '''<thinking>
Let me create a flowchart
</thinking>
```mermaid
flowchart TD
    Start --> End
```''',
        
        # HTML code blocks
        '''<pre><code>
function test() {
    return true;
}
</code></pre>''',
        
        # Mixed content
        '''Here is the code:
```python
x = 1 + 1
```
The result is 2.'''
    ]
    
    print("Testing clean_llm_output function:")
    print("=" * 100)
    
    for i, test_input in enumerate(test_cases):
        print(f"\nTest {i}\n:{test_input}")
        result = clean_llm_output(test_input)
        error = result.pop("error", "")

        if error:
            print(f"Failed to parse:\n\t{test_input}")
            continue
            
        code = result.pop("code", "")
        print(f"\nCode block:\n\n{code}")
        print("\nOther result:\n", result)
        print("-" * 80)
