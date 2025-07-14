import subprocess
import os
import shutil
from pathlib import Path
import streamlit as st

def debug_pandoc_environment():
    """Debug the pandoc environment to identify differences"""
    
    st.write("### 🔍 Environment Debugging")
    
    # Check if pandoc is available
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        st.write("✅ Pandoc found:")
        st.code(result.stdout[:200] + "...")
    except FileNotFoundError:
        st.error("❌ Pandoc not found in subprocess PATH")
        return
    
    # Check available PDF engines
    try:
        result = subprocess.run(['pandoc', '--list-pdf-engines'], capture_output=True, text=True)
        st.write("📄 Available PDF engines:")
        st.code(result.stdout)
    except Exception as e:
        st.warning(f"Could not list PDF engines: {e}")
    
    # Check XeLaTeX availability
    engines_to_check = ['xelatex', 'lualatex', 'pdflatex']
    st.write("🔧 Checking LaTeX engines:")
    
    for engine in engines_to_check:
        try:
            result = subprocess.run([engine, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                st.success(f"✅ {engine} available")
            else:
                st.error(f"❌ {engine} failed: {result.stderr}")
        except FileNotFoundError:
            st.error(f"❌ {engine} not found")
        except subprocess.TimeoutExpired:
            st.warning(f"⚠️ {engine} timeout")
        except Exception as e:
            st.error(f"❌ {engine} error: {e}")
    
    # Check PATH differences
    st.write("🛤️ PATH comparison:")
    subprocess_path = os.environ.get('PATH', '')
    st.write(f"**Subprocess PATH length:** {len(subprocess_path.split(':'))}")
    
    # Check common LaTeX locations
    common_latex_paths = [
        '/usr/bin/xelatex',
        '/usr/local/bin/xelatex', 
        '/opt/texlive/*/bin/*/xelatex',
        '/usr/share/texlive/bin/xelatex'
    ]
    
    st.write("📍 Checking common LaTeX locations:")
    for path in common_latex_paths:
        if '*' in path:
            # Handle glob patterns
            import glob
            matches = glob.glob(path)
            if matches:
                st.success(f"✅ Found: {matches[0]}")
            else:
                st.info(f"➖ Not found: {path}")
        else:
            if Path(path).exists():
                st.success(f"✅ Found: {path}")
            else:
                st.info(f"➖ Not found: {path}")

def fix_pandoc_subprocess_environment():
    """Get the proper environment for pandoc subprocess"""
    
    # Get current environment
    env = os.environ.copy()
    
    # Common LaTeX paths to add
    additional_paths = [
        '/usr/local/texlive/*/bin/*',
        '/opt/texlive/*/bin/*', 
        '/usr/share/texlive/bin',
        '/Library/TeX/texbin',  # macOS
        '/usr/local/bin',
        '/usr/bin'
    ]
    
    # Expand glob patterns and add to PATH
    import glob
    current_path = env.get('PATH', '')
    new_paths = []
    
    for path_pattern in additional_paths:
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            new_paths.extend(matches)
        else:
            if Path(path_pattern).exists():
                new_paths.append(path_pattern)
    
    # Add new paths to beginning of PATH
    if new_paths:
        env['PATH'] = ':'.join(new_paths) + ':' + current_path
    
    # Set TEXMFCACHE to avoid permission issues
    env['TEXMFCACHE'] = '/tmp/texmf-cache'
    
    # Set other helpful LaTeX environment variables
    env['SOURCE_DATE_EPOCH'] = '0'  # For reproducible builds
    
    return env

def run_pandoc_with_better_error_handling(pandoc_cmd, md_filepath, pdf_filepath):
    """Run pandoc with comprehensive error handling and fallbacks"""
    
    st.write("### 🚀 Running Pandoc with Enhanced Error Handling")
    
    # Method 1: Try with enhanced environment
    st.write("**Method 1:** Enhanced environment")
    try:
        env = fix_pandoc_subprocess_environment()
        
        result = subprocess.run(
            pandoc_cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=60,
            cwd=str(Path(md_filepath).parent)  # Set working directory
        )
        
        if result.returncode == 0:
            st.success("✅ Method 1 succeeded!")
            return True, result.stdout
        else:
            st.warning(f"⚠️ Method 1 failed: {result.stderr}")
            
    except Exception as e:
        st.error(f"❌ Method 1 error: {e}")
    
    # Method 2: Try with LuaLaTeX instead of XeLaTeX
    st.write("**Method 2:** LuaLaTeX fallback")
    try:
        lua_cmd = [cmd if cmd != '--pdf-engine=xelatex' else '--pdf-engine=lualatex' 
                   for cmd in pandoc_cmd]
        
        env = fix_pandoc_subprocess_environment()
        result = subprocess.run(
            lua_cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=60
        )
        
        if result.returncode == 0:
            st.success("✅ Method 2 (LuaLaTeX) succeeded!")
            return True, result.stdout
        else:
            st.warning(f"⚠️ Method 2 failed: {result.stderr}")
            
    except Exception as e:
        st.error(f"❌ Method 2 error: {e}")
    
    # Method 3: Try without unicode-math (remove font specifications)
    st.write("**Method 3:** Without unicode-math")
    try:
        simple_cmd = [
            'pandoc',
            str(md_filepath),
            '-o', str(pdf_filepath),
            '--pdf-engine=xelatex',
            '--standalone',
            '-f', 'markdown+tex_math_dollars'
            # Remove font specifications that require unicode-math
        ]
        
        env = fix_pandoc_subprocess_environment()
        result = subprocess.run(
            simple_cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=60
        )
        
        if result.returncode == 0:
            st.success("✅ Method 3 (no unicode-math) succeeded!")
            return True, result.stdout
        else:
            st.warning(f"⚠️ Method 3 failed: {result.stderr}")
            
    except Exception as e:
        st.error(f"❌ Method 3 error: {e}")
    
    # Method 4: Use shell=True (last resort)
    st.write("**Method 4:** Shell execution")
    try:
        cmd_str = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in pandoc_cmd])
        
        env = fix_pandoc_subprocess_environment()
        result = subprocess.run(
            cmd_str,
            capture_output=True, 
            text=True, 
            env=env,
            shell=True,
            timeout=60
        )
        
        if result.returncode == 0:
            st.success("✅ Method 4 (shell) succeeded!")
            return True, result.stdout
        else:
            st.error(f"❌ Method 4 failed: {result.stderr}")
            
    except Exception as e:
        st.error(f"❌ Method 4 error: {e}")
    
    return False, "All methods failed"

def create_minimal_test_case():
    """Create a minimal test case to debug the issue"""
    
    st.write("### 🧪 Creating Minimal Test Case")
    
    # Create minimal markdown file
    test_md = """---
title: "Test Document"
---

Simple test: $E = mc^2$.

Display math:
$$
\\int_0^1 x dx = \\frac{1}{2}
$$
"""
    
    # Save test file
    test_md_path = Path("/tmp/pandoc_test.md")
    test_pdf_path = Path("/tmp/pandoc_test.pdf")
    
    with open(test_md_path, 'w', encoding='utf-8') as f:
        f.write(test_md)
    
    st.write(f"📝 Created test markdown: {test_md_path}")
    
    # Test different pandoc commands
    test_commands = [
        # Minimal command
        ['pandoc', str(test_md_path), '-o', str(test_pdf_path), '--pdf-engine=xelatex'],
        
        # With math support
        ['pandoc', str(test_md_path), '-o', str(test_pdf_path), '--pdf-engine=xelatex', '-f', 'markdown+tex_math_dollars'],
        
        # With fonts
        ['pandoc', str(test_md_path), '-o', str(test_pdf_path), '--pdf-engine=xelatex', '-f', 'markdown+tex_math_dollars', '-V', 'mainfont=Latin Modern Roman'],
        
        # Your original command
        ['pandoc', str(test_md_path), '-o', str(test_pdf_path), '--pdf-engine=xelatex', '--standalone', '-f', 'markdown+tex_math_dollars', '--variable', 'mainfont="Latin Modern Roman"', '--variable', 'mathfont="Latin Modern Math"']
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        st.write(f"**Test {i}:** {' '.join(cmd)}")
        
        try:
            env = fix_pandoc_subprocess_environment()
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode == 0:
                st.success(f"✅ Test {i} passed!")
                if test_pdf_path.exists():
                    st.write(f"📄 PDF size: {test_pdf_path.stat().st_size} bytes")
            else:
                st.error(f"❌ Test {i} failed:")
                st.code(result.stderr)
                
        except Exception as e:
            st.error(f"❌ Test {i} exception: {e}")
        
        # Clean up for next test
        if test_pdf_path.exists():
            test_pdf_path.unlink()

def improved_pandoc_function(md_filepath, pdf_filepath):
    """Improved pandoc function with all fixes applied"""
    
    # Ensure paths are Path objects
    md_filepath = Path(md_filepath)
    pdf_filepath = Path(pdf_filepath)
    
    # Build pandoc command
    pandoc_cmd = [
        'pandoc',
        str(md_filepath),
        '-o', str(pdf_filepath),
        '--pdf-engine=xelatex',
        '--standalone',
        '-f', 'markdown+tex_math_dollars',
        '-V', 'mainfont=Latin Modern Roman',  # Use -V instead of --variable
        '-V', 'mathfont=Latin Modern Math'
    ]
    
    print(f"Running pandoc command: {' '.join(pandoc_cmd)}")
    
    try:
        # Get enhanced environment
        env = fix_pandoc_subprocess_environment()
        
        # Run with proper environment and error handling
        result = subprocess.run(
            pandoc_cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=120,  # Increased timeout
            cwd=str(md_filepath.parent)  # Set working directory
        )
        
        if result.returncode == 0:
            print("✅ Pandoc succeeded")
            return True, str(pdf_filepath)
        else:
            print(f"❌ Pandoc failed: {result.stderr}")
            
            # Try fallback methods
            success, output = run_pandoc_with_better_error_handling(
                pandoc_cmd, md_filepath, pdf_filepath
            )
            
            if success:
                return True, str(pdf_filepath)
            else:
                return False, f"Pandoc error: {result.stderr}"
                
    except subprocess.TimeoutExpired:
        return False, "Pandoc timeout - process took too long"
    except Exception as e:
        return False, f"Pandoc execution error: {str(e)}"

# Streamlit interface for debugging
def main():
    st.title("🔧 Pandoc Subprocess Debugging Tool")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Debug Environment", "🧪 Test Cases", "📚 Solutions"])
    
    with tab1:
        st.header("Environment Analysis")
        if st.button("🔍 Analyze Environment"):
            debug_pandoc_environment()
    
    with tab2:
        st.header("Test Cases")
        if st.button("🧪 Run Test Cases"):
            create_minimal_test_case()
    
    with tab3:
        st.header("Solutions Summary")
        st.markdown("""
        ### 🎯 Key Solutions:
        
        1. **Fix Environment Variables**
           - Add LaTeX paths to subprocess PATH
           - Set TEXMFCACHE for permissions
           - Use enhanced environment in subprocess.run()
        
        2. **Command Format Issues**
           - Use `-V` instead of `--variable`
           - Remove quotes around font names in subprocess
           - Set proper working directory
        
        3. **Fallback Strategies**
           - Try LuaLaTeX if XeLaTeX fails
           - Remove unicode-math requirements if needed
           - Use shell=True as last resort
        
        4. **Error Handling**
           - Increase timeout for LaTeX compilation
           - Capture and parse stderr properly
           - Test with minimal cases first
        """)

if __name__ == "__main__":
    main()
