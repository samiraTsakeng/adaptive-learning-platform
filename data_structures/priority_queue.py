"""
Priority Queue Data Structure

Time Complexity:
  - push(item, priority): O(n) due to sort after insert
  - pop(): O(1) removes from front
  - peek(): O(1)
  - is_empty(): O(1)
  - size(): O(1)

Space Complexity: O(n) where n = number of items

Note: This implementation uses a sorted list. For production, consider heapq for O(log n) push.

Use Case: Rank lessons by performance (higher score = higher priority)
"""


class PriorityQueue:
    def __init__(self):
        """Initialize an empty priority queue. Items sorted by priority (descending)."""
        self.items = []

    def push(self, item, priority):
        """
        Insert an item with a priority.
        
        Time: O(n) due to sort
        Space: O(1)
        Higher priority = processed first.
        """
        self.items.append((priority, item))
        # Sort by priority in descending order (highest first)
        self.items.sort(key=lambda x: x[0], reverse=True)

    def pop(self):
        """
        Remove and return the highest-priority item.
        
        Time: O(1)
        Returns None if empty.
        """
        if not self.is_empty():
            return self.items.pop(0)[1]
        return None

    def peek(self):
        """
        View the highest-priority item without removing.
        
        Time: O(1)
        Returns None if empty.
        """
        if not self.is_empty():
            return self.items[0][1]
        return None

    def is_empty(self):
        """
        Check if queue is empty.
        
        Time: O(1)
        """
        return len(self.items) == 0

    def size(self):
        """
        Return the number of items in the queue.
        
        Time: O(1)
        """
        return len(self.items)
