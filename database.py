# database.py
import json
import os
import sqlite3


def get_db_path() -> str:
    """Get the database path - always in the script's directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "features.db")


def init_db() -> None:
    """Initialize the feature store database with table and sample data"""
    conn = sqlite3.connect(get_db_path())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS features (
            key TEXT PRIMARY KEY,
            vector TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample data for experimentation
    example_features = [
        (
            "user_123",
            "[0.1, 0.2, -0.5, 0.8, 0.3, -0.1, 0.9, -0.4]",
            json.dumps({"type": "user", "id": 123, "segment": "premium"}),
        ),
        (
            "product_abc",
            "[0.7, -0.3, 0.4, 0.1, -0.8, 0.6, 0.2, -0.5]",
            json.dumps({"type": "product", "id": "abc", "category": "electronics"}),
        ),
    ]

    # Insert if not exists
    for key, vector, metadata in example_features:
        try:
            conn.execute(
                "INSERT INTO features (key, vector, metadata) VALUES (?, ?, ?)",
                (key, vector, metadata),
            )
        except sqlite3.IntegrityError:
            pass  # Already exists

    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection"""
    return sqlite3.connect(get_db_path())


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")
