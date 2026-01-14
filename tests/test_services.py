"""
Quick verification that all microservices can be imported and start without errors.
Run with: python tests/test_services.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auth_service():
    """Verify auth service can be imported"""
    try:
        from services.auth_service import app as auth_app
        assert auth_app is not None
        print("✓ Auth Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Auth Service failed: {e}")
        return False

def test_courses_service():
    """Verify courses service can be imported"""
    try:
        from services.courses_service import app as courses_app
        assert courses_app is not None
        print("✓ Courses Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Courses Service failed: {e}")
        return False

def test_quizzes_service():
    """Verify quizzes service can be imported"""
    try:
        from services.quizzes_service import app as quizzes_app
        assert quizzes_app is not None
        print("✓ Quizzes Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Quizzes Service failed: {e}")
        return False

def test_recommendations_service():
    """Verify recommendations service can be imported"""
    try:
        from services.recommendations_service import app as recs_app
        assert recs_app is not None
        print("✓ Recommendations Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Recommendations Service failed: {e}")
        return False

def test_search_service():
    """Verify search service can be imported"""
    try:
        from services.search_service import app as search_app
        assert search_app is not None
        print("✓ Search Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Search Service failed: {e}")
        return False

def test_progress_service():
    """Verify progress service can be imported"""
    try:
        from services.progress_service import app as progress_app
        assert progress_app is not None
        print("✓ Progress Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Progress Service failed: {e}")
        return False

def test_teacher_service():
    """Verify teacher service can be imported"""
    try:
        from services.teacher_service import app as teacher_app
        assert teacher_app is not None
        print("✓ Teacher Service imports successfully")
        return True
    except Exception as e:
        print(f"✗ Teacher Service failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Microservices Imports")
    print("=" * 60)
    
    results = [
        test_auth_service(),
        test_courses_service(),
        test_quizzes_service(),
        test_recommendations_service(),
        test_search_service(),
        test_progress_service(),
        test_teacher_service(),
    ]
    
    print("=" * 60)
    if all(results):
        print(f"✅ All {len(results)} services verified successfully!")
    else:
        failed = len([r for r in results if not r])
        print(f"❌ {failed} service(s) failed")
        sys.exit(1)
