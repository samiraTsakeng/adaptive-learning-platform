import os
import sys
import shutil
import time

# Ensure project root is on sys.path when running script directly
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

# Import project modules
from backend.database import DB_PATH, create_tables
from backend.data.sample_data import insert_sample_data


def backup_db():
	"""Create a timestamped backup of the existing database file if present."""
	if os.path.exists(DB_PATH):
		ts = time.strftime("%Y%m%d%H%M%S")
		backup_path = DB_PATH + f".bak.{ts}"
		os.makedirs(os.path.dirname(backup_path), exist_ok=True)
		shutil.copy2(DB_PATH, backup_path)
		print(f"Backup created: {backup_path}")
	else:
		print("No existing database file to backup.")


def reset_db(remove_file=True):
	"""Remove existing DB file (if remove_file=True), recreate schema, and load sample data."""
	if remove_file and os.path.exists(DB_PATH):
		try:
			os.remove(DB_PATH)
			print("Removed existing database file.")
		except Exception as e:
			print(f"Warning: could not remove DB file: {e}")

	# Recreate schema and load sample data
	create_tables()
	insert_sample_data()
	print("Database reset and sample data loaded.")


if __name__ == "__main__":
    response = input("⚠️  This will delete all quiz results and user progress. Backup will be created. Continue? (yes/no): ")
    if response.strip().lower() == 'yes':
        backup_db()
        reset_db()
        print("✅ Database reset complete.")
    else:
        print("Reset cancelled.")
