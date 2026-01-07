"""
Hash Table (Dictionary-based) Data Structure

Time Complexity (Average Case):
  - insert(key, value): O(1) amortized
  - get(key): O(1) average
  - exists(key): O(1) average
  - remove(key): O(1) average

Time Complexity (Worst Case):
  - All operations: O(n) if many hash collisions

Space Complexity: O(n) where n = number of key-value pairs

Use Case: Fast lookup of users by username (auth cache)
"""


class HashTable:
    def __init__(self):
        """Initialize empty hash table using Python dict (built-in hash table)."""
        self.table = {}

    def insert(self, key, value):
        """
        Insert or update a key-value pair.
        
        Time: O(1) average
        """
        self.table[key] = value

    def get(self, key):
        """
        Retrieve value by key.
        
        Time: O(1) average
        Returns None if key not found.
        """
        return self.table.get(key)

    def exists(self, key):
        """
        Check if key exists.
        
        Time: O(1) average
        """
        return key in self.table

    def remove(self, key):
        """
        Remove a key-value pair.
        
        Time: O(1) average
        """
        if key in self.table:
            del self.table[key]

    def size(self):
        """Return number of entries."""
        return len(self.table)
