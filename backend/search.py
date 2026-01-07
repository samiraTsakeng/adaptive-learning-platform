"""
Course & Lesson Search using Trie data structure.

Time Complexity:
  - build_search_index(courses): O(c + l) where c = courses, l = lessons
  - search_courses(query): O(m) where m = length of query
  - search_lessons(query): O(m + n) where m = length of query, n = matching results
  
Uses a Trie for prefix-based search of courses and lessons.
"""

from data_structures.trie import Trie
from backend.database import connect_db, get_all_courses, get_lessons_by_course


class SearchIndex:
    def __init__(self):
        self.course_trie = Trie()
        self.lesson_trie = Trie()
        # Store metadata for quick lookup
        self.course_meta = {}  # title -> (id, description)
        self.lesson_meta = {}  # title -> (id, course_id, content)

    def build_index(self):
        """
        Build search index from database.
        
        Time: O(c + l) where c = courses, l = lessons
        Space: O(c + l)
        """
        # Index courses
        courses = get_all_courses()
        for course_id, title, description in courses:
            self.course_trie.insert(title)
            self.course_meta[title.lower()] = (course_id, description)

        # Index lessons (per course)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, title, course_id, content FROM lessons")
        lessons = cur.fetchall()
        conn.close()

        for lesson_id, title, course_id, content in lessons:
            self.lesson_trie.insert(title)
            self.lesson_meta[title.lower()] = (lesson_id, course_id, content)

    def search_courses(self, query):
        """
        Search for courses by prefix.
        
        Time: O(m + n) where m = query length, n = matching courses
        Space: O(n)
        
        Returns list of (course_id, title, description).
        """
        matches = self.course_trie.get_all_words_with_prefix(query)
        results = []
        for title in matches:
            course_id, description = self.course_meta[title.lower()]
            results.append((course_id, title, description))
        return results

    def search_lessons(self, query):
        """
        Search for lessons by prefix.
        
        Time: O(m + n) where m = query length, n = matching lessons
        Space: O(n)
        
        Returns list of (lesson_id, title, course_id).
        """
        matches = self.lesson_trie.get_all_words_with_prefix(query)
        results = []
        for title in matches:
            lesson_id, course_id, content = self.lesson_meta[title.lower()]
            results.append((lesson_id, title, course_id))
        return results


# Global search index (lazy-loaded)
_search_index = None


def get_search_index():
    """Lazy-load the global search index."""
    global _search_index
    if _search_index is None:
        _search_index = SearchIndex()
        _search_index.build_index()
    return _search_index


def search_courses(query):
    """
    Public function to search courses.
    
    Time: O(m + n) where m = query length, n = results
    """
    idx = get_search_index()
    return idx.search_courses(query)


def search_lessons(query):
    """
    Public function to search lessons.
    
    Time: O(m + n) where m = query length, n = results
    """
    idx = get_search_index()
    return idx.search_lessons(query)
