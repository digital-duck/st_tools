"""
Comprehensive test cases for clean_llm_output function
"""

test_cases = [
    # Test 0: Basic mermaid with thinking
    '''<thinking>Need to create a workflow</thinking>
```mermaid
flowchart TD
    A --> B
```''',
    
    # Test 1: Python code with markdown
    '```python\nprint("hello world")\n```',
    
    # Test 2: SQL with explanation
    '''Here's the SQL:
```sql
select count(*) from t_customers;
```
''',
    
    # Test 3: Multiple code blocks
    '''```python
def hello():
    return "world"
```

```javascript
console.log("hello");
```''',

    # Test 4: Javascript code blocks
    '''
```javascript
console.log("hello");
```''',
    
    # Test 5: With thinking tags
    '''<thinking>
Let me create a flowchart
</thinking>
```mermaid
flowchart TD
    Start --> End
```''',
    
    # Test 6: HTML code blocks
    '''<pre><code>
function test() {
    return true;
}
</code></pre>''',
    
    # Test 7: Mixed content
    '''Here is the code:
```python
x = 1 + 1
```
The result is 2.''',

    # Test 8: Sequence diagram
    '''```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob!
    B->>A: Hi Alice!
```''',

    # Test 9: Multiple XML tags
    '''<thinking>Planning the approach</thinking>
<reasoning>This needs a state diagram</reasoning>
<analysis>User wants authentication flow</analysis>
```mermaid
stateDiagram
    [*] --> Login
    Login --> Dashboard
```''',

    # Test 10: HTML with DOCTYPE
    '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>Hello World</body>
</html>''',

    # Test 11: JSON data
    '''```json
{
  "name": "test",
  "version": "1.0",
  "dependencies": []
}
```''',

    # Test 12: YAML configuration
    '''```yaml
name: deploy-workflow
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
```''',

    # Test 13: CSS styles
    '''```css
.container {
    display: flex;
    justify-content: center;
    align-items: center;
}

#main-header {
    background-color: #333;
    color: white;
}
```''',

    # Test 14: SQL with complex queries
    '''```sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC;
```''',

    # Test 15: Python with comments (test preserve_comments)
    '''```python
# This is a sample function
def calculate_total(items):
    """Calculate total price of items."""
    total = 0  # Initialize counter
    for item in items:
        total += item.price  # Add item price
    return total
```''',

    # Test 16: Mixed content with reasoning
    '''<reasoning>
The user wants to create a deployment pipeline.
I should create a flowchart showing the stages.
</reasoning>

Here's the deployment workflow:

```mermaid
flowchart LR
    A[Code Commit] --> B[Build]
    B --> C[Test]
    C --> D{Tests Pass?}
    D -->|Yes| E[Deploy]
    D -->|No| F[Fix Issues]
    F --> B
```

This shows the continuous integration process.''',

    # Test 17: No code fences, just mermaid keywords
    '''I need a simple flowchart:

flowchart TD
    Start --> Process
    Process --> End''',

    # Test 18: JavaScript with modern syntax
    '''```javascript
const processData = async (data) => {
    const result = await fetch('/api/process', {
        method: 'POST',
        body: JSON.stringify(data)
    });
    return result.json();
};

// Arrow function example
const multiply = (a, b) => a * b;
```''',

    # Test 19: Markdown content
    '''```markdown
# My Project

This is a **test** document with:

- List item 1
- List item 2

## Code Example

`inline code` and code blocks.
```''',

    # Test 20: HTML with embedded JavaScript
    '''```html
<script>
function handleClick() {
    console.log("Button clicked!");
    document.getElementById("demo").innerHTML = "Hello!";
}
</script>
<button onclick="handleClick()">Click me</button>
<p id="demo">Original text</p>
```''',

    # Test 21: Empty input
    '',

    # Test 22: Only whitespace
    '   \n\t  \n   ',

    # Test 23: Unknown content type
    '''This is just plain text without any code fences or special markers.
It should trigger the unknown content warning and use basic cleaning.
No programming languages or mermaid keywords here.''',

    # Test 24: Gantt chart
    '''```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Development
    Requirements : done, req, 2024-01-01, 2024-01-15
    Design      : active, des, 2024-01-16, 2024-02-01
    Coding      : cod, after des, 30d
```''',

    # Test 25: Malformed XML tags
    '''<thinking>Incomplete tag
```python
print("test")
```
Some text after</thinking>''',

    # Test 26: Multiple language detection edge case
    '''Here's some code that might confuse the detector:

```python
# This looks like python
def function():
    console.log("but has javascript inside")
    SELECT * FROM users;  # and SQL too!
```''',

    # Test 27: Very long code with explanations
    '''This is a comprehensive example:

```python
class DataProcessor:
    """A class for processing data."""
    
    def __init__(self, config):
        self.config = config
        self.data = []
    
    def load_data(self, filename):
        """Load data from file."""
        with open(filename, 'r') as f:
            self.data = f.readlines()
    
    def process(self):
        """Process the loaded data."""
        processed = []
        for line in self.data:
            cleaned = line.strip().lower()
            processed.append(cleaned)
        return processed
```

This class provides a simple interface for data processing tasks.
The result will be a list of cleaned strings.''',

    # Test 28: Journey diagram
    '''```mermaid
journey
    title User Shopping Experience
    section Browse
      Go to website: 5: Me
      Search products: 3: Me
      View details: 4: Me
    section Purchase
      Add to cart: 5: Me
      Checkout: 2: Me
      Payment: 1: Me, Bank
```''',

    # Test 29: Class diagram
    '''```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog
```''',

    # Test 30: Git graph
    '''```mermaid
gitgraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```''',

    # Test 31: Mixed JavaScript and Python detection
    '''```javascript
// This should be detected as JavaScript
function processData() {
    const data = fetch('/api/data');
    return data.json();
}

// But contains python-like syntax
def helper():
    pass
```''',

    # Test 32: Complex mermaid with explanatory text
    '''Let me explain the authentication flow:

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated
    Unauthenticated --> Authenticating: login()
    Authenticating --> Authenticated: success
    Authenticating --> Unauthenticated: failure
    Authenticated --> Unauthenticated: logout()
    
    state Authenticated {
        [*] --> Active
        Active --> Idle: timeout
        Idle --> Active: activity
    }
```

This diagram shows how users transition between authentication states.
The nested state shows activity tracking within the authenticated state.''',

    # Test 33: Code with multiple comment styles
    '''```python
#!/usr/bin/env python3
"""
Module docstring
Multi-line documentation
"""

# Single line comment
def process(data):
    # Another comment
    result = []  # Inline comment
    """
    Multi-line string that looks like comment
    """
    return result
```''',

    # Test 34: Multiple analysis tags
    '''<analysis>
The user needs a complex workflow that handles multiple conditions.
This requires careful state management and error handling.
</analysis>

<thinking>
I should create a comprehensive flowchart that shows:
1. Input validation
2. Processing steps  
3. Error handling
4. Output generation
</thinking>

<reasoning>
A flowchart is the best choice because it clearly shows:
- Decision points
- Alternative paths
- Error conditions
- Final outcomes
</reasoning>

```mermaid
flowchart TD
    A[Input Data] --> B{Valid?}
    B -->|No| C[Show Error]
    B -->|Yes| D[Process Data]
    D --> E{Success?}
    E -->|No| F[Log Error]
    E -->|Yes| G[Return Result]
    C --> H[End]
    F --> H
    G --> H
```''',

    # Test 35: No fences, complex mermaid
    '''Creating a user registration flowchart:

sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database
    
    U->>F: Enter registration details
    F->>B: POST /api/register
    B->>D: Check if user exists
    D-->>B: User status
    alt User doesn't exist
        B->>D: Create user
        D-->>B: User created
        B-->>F: Success response
        F-->>U: Registration successful
    else User exists
        B-->>F: Error response
        F-->>U: User already exists
    end''',
]