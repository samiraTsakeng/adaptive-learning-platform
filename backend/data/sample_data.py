from ..database import connect_db


def insert_sample_data():
    """Disabled: only teacher-uploaded courses appear."""
    conn = connect_db()
    cursor = conn.cursor()

    
    conn.close()
    print("✅ Database initialized (no sample data - teachers must create courses)")


if __name__ == "__main__":
    insert_sample_data()
