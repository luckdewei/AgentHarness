"""
Tests for demo_pkg.utils.
"""

from demo_pkg.utils import greet, add


def test_greet():
    assert greet("World") == "Hello, World!"
    assert greet("Agent") == "Hello, Agent!"


def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
