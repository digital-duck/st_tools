import re

def strip_md_xml_tag(code: str) -> str:
    """
    Remove markdown code fences, thinking tags, and other common LLM output artifacts.
    
    Args:
        code (str): Input code string with potential markdown/XML tags
        
    Returns:
        str: Cleaned code string
        
    Examples:
        >>> strip_md_xml_tag('```python\\nprint("hello")\\n```')
        'print("hello")'
        
        >>> strip_md_xml_tag('```mermaid\\nflowchart TD\\n```')
        'flowchart TD'
    """
    if not code:
        return ""
    
    # Remove thinking tags (preserving content inside)
    code = re.sub(r'<thinking>.*?</thinking>', '', code, flags=re.DOTALL | re.IGNORECASE)
    code = re.sub(r'</?thinking>', '', code, flags=re.IGNORECASE)
    
    # Remove markdown code fences with language specifiers
    # Handles: ```python, ```mermaid, ```javascript, etc.
    code = re.sub(r'```\w*\n?', '', code, flags=re.IGNORECASE)
    
    # Remove standalone closing code fences
    code = re.sub(r'```\n?', '', code)
    
    # Remove HTML/XML-style code blocks
    code = re.sub(r'</?code[^>]*>', '', code, flags=re.IGNORECASE)
    code = re.sub(r'</?pre[^>]*>', '', code, flags=re.IGNORECASE)
    
    # Remove common LLM explanation prefixes
    code = re.sub(r'^(Here\'s|Here is|This is|The code is).*?:\s*\n?', '', code, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove trailing explanations that start with new lines
    code = re.sub(r'\n\n+(This code|The above|Explanation:|Note:).*$', '', code, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up extra whitespace
    code = code.strip()
    
    return code


def strip_md_xml_tag_advanced(code: str, preserve_comments: bool = True) -> str:
    """
    Advanced version with more comprehensive cleaning options.
    
    Args:
        code (str): Input code string
        preserve_comments (bool): Whether to preserve code comments
        
    Returns:
        str: Cleaned code string
    """
    if not code:
        return ""
    
    original_code = code
    
    # Remove various thinking/reasoning tags
    thinking_patterns = [
        r'<thinking>.*?</thinking>',
        r'<reasoning>.*?</reasoning>',
        r'<analysis>.*?</analysis>',
        r'</?(?:thinking|reasoning|analysis)>'
    ]
    
    for pattern in thinking_patterns:
        code = re.sub(pattern, '', code, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove markdown code fences with any language
    code_fence_patterns = [
        r'```\w+\n?',  # ```python, ```mermaid, etc.
        r'```\n?',     # Plain ```
        r'~~~\w*\n?',  # Alternative tildes syntax
        r'~~~\n?'
    ]
    
    for pattern in code_fence_patterns:
        code = re.sub(pattern, '', code, flags=re.IGNORECASE)
    
    # Remove HTML/XML code block tags
    html_patterns = [
        r'</?code[^>]*>',
        r'</?pre[^>]*>',
        r'</?script[^>]*>',
        r'</?style[^>]*>'
    ]
    
    for pattern in html_patterns:
        code = re.sub(pattern, '', code, flags=re.IGNORECASE)
    
    # Remove common LLM explanation patterns
    explanation_patterns = [
        r'^(Here\'s|Here is|This is|The code is|Below is).*?:\s*\n?',
        r'^(Let me|I\'ll|I will).*?\n?',
        r'\n\n+(This|The above|Explanation|Note|Important).*$',
        r'^Output:\s*\n?',
        r'^Result:\s*\n?'
    ]
    
    for pattern in explanation_patterns:
        code = re.sub(pattern, '', code, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    # Remove citation tags if present
    code = re.sub(r']*>.*?', '', code, flags=re.DOTALL)
    
    # Clean up whitespace
    code = code.strip()
    
    # If result is empty or too different, return original
    if not code or len(code) < len(original_code) * 0.1:
        return original_code.strip()
    
    return code


def strip_specific_language_tags(code: str, languages: list = None) -> str:
    """
    Remove markdown tags for specific programming languages only.
    
    Args:
        code (str): Input code string
        languages (list): List of languages to strip (default: common ones)
        
    Returns:
        str: Code with only specified language tags removed
    """
    if not code:
        return ""
    
    if languages is None:
        languages = ['python', 'javascript', 'js', 'mermaid', 'html', 'css', 'json', 'yaml', 'sql']
    
    # Create pattern for specified languages
    lang_pattern = '|'.join(re.escape(lang) for lang in languages)
    pattern = rf'```(?:{lang_pattern})\n?'
    
    # Remove opening tags for specified languages
    code = re.sub(pattern, '', code, flags=re.IGNORECASE)
    
    # Remove closing tags
    code = re.sub(r'```\n?', '', code)
    
    return code.strip()


def clean_llm_output(text: str, content_type: str = "code") -> str:
    """
    Comprehensive cleaner for different types of LLM output.
    
    Args:
        text (str): Raw LLM output
        content_type (str): Type of content - 'code', 'mermaid', 'text', 'mixed'
        
    Returns:
        str: Cleaned output appropriate for the content type
    """
    if not text:
        return ""
    
    if content_type == "mermaid":
        # Specific cleaning for Mermaid diagrams
        text = strip_md_xml_tag_advanced(text)
        
        # Remove common Mermaid explanations
        text = re.sub(r'^.*?(flowchart|sequenceDiagram|stateDiagram|gantt)', r'\1', text, flags=re.IGNORECASE)
        
        # Ensure it starts with a valid Mermaid diagram type
        mermaid_types = ['flowchart', 'sequenceDiagram', 'stateDiagram', 'gantt', 'journey', 'gitgraph', 'classDiagram']
        
        for diagram_type in mermaid_types:
            if diagram_type.lower() in text.lower():
                # Find and extract the diagram part
                pattern = rf'({re.escape(diagram_type)}.*?)(?:\n\n|$)'
                match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return text.strip()
    
    elif content_type == "code":
        # For programming code
        return strip_md_xml_tag_advanced(text, preserve_comments=True)
    
    elif content_type == "text":
        # For plain text, only remove thinking tags
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()
    
    else:  # mixed content
        return strip_md_xml_tag_advanced(text)


# Test cases and examples
if __name__ == "__main__":
    test_cases = [
        # Python code with markdown
        '```python\nprint("hello world")\n```',
        
        # Mermaid with explanation
        '''Here's the Mermaid diagram:
```mermaid
flowchart TD
    A --> B
```
This diagram shows a simple flow.''',
        
        # Multiple code blocks
        '''```python
def hello():
    return "world"
```

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
    
    print("Testing strip_md_xml_tag function:")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input:  {repr(test)}")
        
        result_basic = strip_md_xml_tag(test)
        result_advanced = strip_md_xml_tag_advanced(test)
        result_mermaid = clean_llm_output(test, "mermaid")
        
        print(f"Basic:    {repr(result_basic)}")
        print(f"Advanced: {repr(result_advanced)}")
        print(f"Mermaid:  {repr(result_mermaid)}")
        print("-" * 40)