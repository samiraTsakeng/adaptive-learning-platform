"""
Trie (Prefix Tree) Data Structure

Time Complexity:
  - insert(word): O(m) where m = length of word
  - search(word): O(m) where m = length of word
  - startswith(prefix): O(m) where m = length of prefix
  - get_all_words_with_prefix(prefix): O(n + m) where n = total words, m = prefix length

Space Complexity: O(ALPHABET_SIZE * m * n) where n = number of words, m = avg word length
"""


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None  # store the full word for quick retrieval


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """
        Insert a word into the Trie.
        
        Time: O(m) where m = length of word
        Space: O(m) for the path
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word

    def search(self, word):
        """
        Search for an exact word.
        
        Time: O(m) where m = length of word
        """
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def startswith(self, prefix):
        """
        Check if any word starts with the given prefix.
        
        Time: O(m) where m = length of prefix
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def get_all_words_with_prefix(self, prefix):
        """
        Retrieve all words starting with the given prefix.
        
        Time: O(n + m) where n = number of matching words, m = prefix length
        Space: O(n) for the result list
        """
        results = []
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return results
            node = node.children[char]

        # DFS to collect all words from this node
        self._dfs(node, results)
        return results

    def _dfs(self, node, results):
        """Helper DFS to collect all complete words under a node."""
        if node.is_end:
            results.append(node.word)
        for child in node.children.values():
            self._dfs(child, results)
