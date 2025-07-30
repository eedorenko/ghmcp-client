#!/usr/bin/env python3
"""
Test script for hello_world.py

Simple test to verify the hello world program works correctly.
"""

import subprocess
import sys
import os

def test_hello_world():
    """Test that hello_world.py runs and produces expected output."""
    
    # Path to hello_world.py
    script_path = os.path.join(os.path.dirname(__file__), 'hello_world.py')
    
    try:
        # Run the hello_world.py script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, check=True)
        
        # Check that it executed successfully
        assert result.returncode == 0, f"Script failed with return code {result.returncode}"
        
        # Check that it contains expected output
        output = result.stdout.strip()
        expected_lines = [
            "Hello, World!",
            "Welcome to the GitHub MCP Client repository!",
            "This is a simple Python hello world program."
        ]
        
        for expected_line in expected_lines:
            assert expected_line in output, f"Expected '{expected_line}' not found in output: {output}"
        
        print("✅ hello_world.py test passed!")
        print(f"📝 Output:\n{output}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ hello_world.py test failed with error: {e}")
        print(f"📝 stdout: {e.stdout}")
        print(f"📝 stderr: {e.stderr}")
        return False
    except AssertionError as e:
        print(f"❌ hello_world.py test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing hello_world.py: {e}")
        return False

if __name__ == "__main__":
    success = test_hello_world()
    sys.exit(0 if success else 1)