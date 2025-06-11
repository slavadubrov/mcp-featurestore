# database.py

import sqlite3
import os


def get_db_path():
    """Get the database path - always in the script's directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "features.db")


def init_db():
    """Initialize the feature store database"""
    conn = sqlite3.connect(get_db_path())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS features (
            key TEXT PRIMARY KEY,
            vector TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add example features for experimentation
    example_features = [
        (
            "user_123", 
            "[0.1, 0.2, -0.5, 0.8, 0.3, -0.1, 0.9, -0.4]",
            '{"type": "user_embedding", "user_id": 123, "age": 25, '
            '"category": "premium"}'
        ),
        (
            "product_abc", 
            "[0.7, -0.3, 0.4, 0.1, -0.8, 0.6, 0.2, -0.5]",
            '{"type": "product_embedding", "product_id": "abc", '
            '"price": 29.99, "category": "electronics"}'
        ),
        (
            "doc_guide_001", 
            "[-0.2, 0.5, 0.9, -0.1, 0.4, 0.7, -0.6, 0.3]",
            '{"type": "document_embedding", "doc_id": "guide_001", '
            '"title": "Getting Started Guide", "section": "introduction"}'
        ),
        (
            "recommendation_engine", 
            "[0.4, 0.8, -0.2, 0.6, -0.7, 0.1, 0.5, -0.9]",
            '{"type": "model_embedding", "model": "collaborative_filter", '
            '"version": "1.2", "accuracy": 0.85}'
        )
    ]
    
    # Insert example features only if they don't exist
    for key, vector, metadata in example_features:
        existing = conn.execute(
            "SELECT 1 FROM features WHERE key = ?", (key,)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO features (key, vector, metadata) "
                "VALUES (?, ?, ?)",
                (key, vector, metadata)
            )
    
    conn.commit()
    conn.close()


def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(get_db_path())


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
