#!/usr/bin/env python3
"""
Simple Hello World Python program.

This module provides a basic hello world functionality with a simple function
that can be imported and used by other modules.
"""


def hello_world():
    """
    Return a simple greeting message.
    
    Returns:
        str: A hello world greeting message.
    """
    return "Hello, World!"


def hello_user(name):
    """
    Return a personalized greeting message.
    
    Args:
        name (str): The name of the person to greet.
        
    Returns:
        str: A personalized greeting message.
    """
    if not name:
        return "Hello, anonymous user!"
    return f"Hello, {name}!"


def main():
    """Main function to demonstrate the hello world functionality."""
    print(hello_world())
    print(hello_user("Python Developer"))


if __name__ == "__main__":
    main()