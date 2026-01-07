"""
Stack (LIFO - Last In, First Out) Data Structure

Time Complexity:
  - push(item): O(1) amortized (list append)
  - pop(): O(1)
  - peek(): O(1)
  - is_empty(): O(1)
  - size(): O(1)

Space Complexity: O(n) where n = number of items

Use Case: Manage quiz question flow (load questions in reverse onto stack)
"""


class Stack:
    def __init__(self):
        """Initialize an empty stack using a list."""
        self.items = []

    def push(self, item):
        """
        Push an item onto the stack (top).
        
        Time: O(1) amortized
        """
        self.items.append(item)

    def pop(self):
        """
        Pop and return the top item from the stack.
        
        Time: O(1)
        Returns None if stack is empty.
        """
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """
        Peek at the top item without removing it.
        
        Time: O(1)
        Returns None if stack is empty.
        """
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        """
        Check if stack is empty.
        
        Time: O(1)
        """
        return len(self.items) == 0

    def size(self):
        """
        Return the number of items in the stack.
        
        Time: O(1)
        """
        return len(self.items)
