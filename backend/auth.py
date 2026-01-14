import hashlib
from .database import connect_db
from data_structures.hash_table import HashTable

USERS_HASH = None


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def load_users_into_hash_table():
    """Load all users from the database into an in-memory HashTable."""
    global USERS_HASH
    USERS_HASH = HashTable()
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT username, password FROM users")
    for username, password in cur.fetchall():
        USERS_HASH.insert(username, password)
    conn.close()


def register_user(username: str, password: str, role: str = 'student'):
    """Register a new user. Returns (success: bool, message: str).

    role: either 'student' or 'teacher'
    """
    hashed = _hash_password(password)
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed, role))
        conn.commit()
        # update in-memory cache if present
        global USERS_HASH
        if USERS_HASH is not None:
            USERS_HASH.insert(username, hashed)
        return True, "✅ User registered"
    except Exception as e:
        # assume uniqueness constraint violation
        return False, f"❌ {str(e)}"
    finally:
        conn.close()


def login_user(username: str, password: str):
    """Attempt to login. Returns (success: bool, result_or_message).
    On success returns (True, username). On failure returns (False, message).
    """
    hashed = _hash_password(password)
    global USERS_HASH
    # check in-memory cache first
    if USERS_HASH is not None and USERS_HASH.exists(username):
        stored = USERS_HASH.get(username)
        if stored == hashed:
            return True, username
        return False, "Invalid credentials"

    # fallback to DB lookup
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "User not found"
    stored = row[0]
    if stored == hashed:
        return True, username
    return False, "Invalid credentials"
