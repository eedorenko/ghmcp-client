#!/usr/bin/env python3
"""
Test cases for hello_world module.

This test module validates the functionality of the hello_world module
using Python's built-in unittest framework.
"""

import sys
import unittest
import io
from unittest.mock import patch

# Import the module we're testing
from hello_world import hello_world, hello_user, main


class TestHelloWorld(unittest.TestCase):
    """Test cases for hello world functionality."""
    
    def test_hello_world_returns_correct_message(self):
        """Test that hello_world() returns the expected greeting."""
        result = hello_world()
        self.assertEqual(result, "Hello, World!")
        self.assertIsInstance(result, str)
    
    def test_hello_user_with_name(self):
        """Test hello_user() with a valid name."""
        result = hello_user("Alice")
        self.assertEqual(result, "Hello, Alice!")
        
        result = hello_user("Bob")
        self.assertEqual(result, "Hello, Bob!")
    
    def test_hello_user_with_empty_string(self):
        """Test hello_user() with an empty string."""
        result = hello_user("")
        self.assertEqual(result, "Hello, anonymous user!")
    
    def test_hello_user_with_none(self):
        """Test hello_user() with None."""
        result = hello_user(None)
        self.assertEqual(result, "Hello, anonymous user!")
    
    def test_hello_user_with_special_characters(self):
        """Test hello_user() with special characters in name."""
        result = hello_user("João")
        self.assertEqual(result, "Hello, João!")
        
        result = hello_user("Mary-Jane")
        self.assertEqual(result, "Hello, Mary-Jane!")
    
    def test_main_function_output(self):
        """Test that main() prints the expected output."""
        # Capture stdout to test print statements
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            main()
        
        output = captured_output.getvalue()
        expected_lines = [
            "Hello, World!",
            "Hello, Python Developer!"
        ]
        
        for expected_line in expected_lines:
            self.assertIn(expected_line, output)


class TestHelloWorldIntegration(unittest.TestCase):
    """Integration tests for hello world module."""
    
    def test_module_can_be_imported(self):
        """Test that the module can be imported successfully."""
        # This test passes if we got here without ImportError
        self.assertTrue(True)
    
    def test_functions_exist(self):
        """Test that all expected functions exist in the module."""
        # Check that functions are callable
        self.assertTrue(callable(hello_world))
        self.assertTrue(callable(hello_user))
        self.assertTrue(callable(main))


def run_tests():
    """Run all tests and return the result."""
    print("Running Hello World Tests")
    print("=" * 30)
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestHelloWorld))
    suite.addTests(loader.loadTestsFromTestCase(TestHelloWorldIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Hello World Test Script")
        print("Usage:")
        print("  python test_hello_world.py")
        print("  python -m unittest test_hello_world")
        print("")
        print("This script tests the hello_world module functionality.")
    else:
        success = run_tests()
        sys.exit(0 if success else 1)