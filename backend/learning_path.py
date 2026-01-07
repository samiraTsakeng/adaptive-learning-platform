"""
Learning Path Graph using Graph data structure.

Time Complexity:
  - build_course_graph(course_id): O(m) where m = lessons in course
  - get_learning_path(start_lesson_id, end_lesson_id): O(m + e) DFS/BFS where e = edges
  
Models lesson prerequisites as a directed graph.
For now, we assume linear prerequisites (lesson N → lesson N+1).
Can be extended to arbitrary prerequisites.
"""

from data_structures.graph import Graph
from backend.database import get_lessons_by_course


def build_course_graph(course_id):
    """
    Build a graph representing lesson prerequisites for a course.
    
    Assumes linear ordering: lesson 1 → lesson 2 → lesson 3, etc.
    Can be extended to read prerequisite data from DB.
    
    Time: O(m) where m = lessons in course
    Space: O(m)
    """
    g = Graph()
    lessons = get_lessons_by_course(course_id)

    # Add all lessons as nodes
    for lesson in lessons:
        g.add_node(lesson[0])

    # Add edges: lesson i → lesson i+1 (linear progression)
    for idx in range(len(lessons) - 1):
        from_lesson = lessons[idx][0]
        to_lesson = lessons[idx + 1][0]
        g.add_edge(from_lesson, to_lesson)

    return g


def get_learning_path(course_id, start_lesson_id):
    """
    Get the learning path (sequence of lessons) from a starting lesson to the end.
    
    Uses DFS to traverse the graph.
    
    Time: O(m + e) where m = lessons, e = edges (typically O(m) for linear graphs)
    Space: O(m) for the result
    
    Returns list of lesson IDs in order.
    """
    g = build_course_graph(course_id)
    path = g.dfs(start_lesson_id)
    return path


def get_next_lesson_in_path(course_id, current_lesson_id):
    """
    Get the next lesson after the current one.
    
    Time: O(1)
    Space: O(1)
    """
    lessons = get_lessons_by_course(course_id)
    lesson_ids = [l[0] for l in lessons]

    try:
        idx = lesson_ids.index(current_lesson_id)
        if idx + 1 < len(lesson_ids):
            return lesson_ids[idx + 1]
    except ValueError:
        pass

    return None
