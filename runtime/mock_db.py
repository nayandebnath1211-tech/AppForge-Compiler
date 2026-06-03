import sqlite3
from typing import List, Dict, Any, Tuple
from pipeline.models import DbSchema

class MockDatabase:
    """
    Simulates a running database by creating an in-memory SQLite database 
    based on the generated DbSchema config, and seeding it with mock data.
    """
    def __init__(self, schema: DbSchema):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.schema = schema
        self._init_db()
        self._seed_data()

    def _init_db(self):
        cursor = self.conn.cursor()
        for table in self.schema.tables:
            columns_sql = []
            for col in table.columns:
                col_def = f"{col.name} {col.type}"
                if col.is_primary_key:
                    col_def += " PRIMARY KEY"
                    # Auto increment integers for primary key in SQLite
                    if col.type == "INTEGER":
                        col_def += " AUTOINCREMENT"
                if not col.is_nullable:
                    col_def += " NOT NULL"
                if col.is_unique:
                    col_def += " UNIQUE"
                if col.default_value is not None:
                    if isinstance(col.default_value, str):
                        col_def += f" DEFAULT '{col.default_value}'"
                    else:
                        col_def += f" DEFAULT {col.default_value}"
                columns_sql.append(col_def)

            # Build foreign keys
            for fk in table.foreign_keys:
                fk_def = f"FOREIGN KEY({fk.column}) REFERENCES {fk.reference_table}({fk.reference_column})"
                columns_sql.append(fk_def)

            create_sql = f"CREATE TABLE IF NOT EXISTS {table.name} (\n  " + ",\n  ".join(columns_sql) + "\n);"
            cursor.execute(create_sql)
            
            # Create indexes
            for idx in table.indexes:
                idx_sql = f"CREATE INDEX IF NOT EXISTS idx_{table.name}_{idx} ON {table.name}({idx});"
                cursor.execute(idx_sql)
                
        self.conn.commit()

    def _seed_data(self):
        """Seeds the created database tables with standard sample datasets."""
        cursor = self.conn.cursor()
        # Seed users if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        if "users" in tables:
            users_data = [
                (1, "admin@appforge.com", "hash", "Admin", "premium"),
                (2, "member@appforge.com", "hash", "Member", "free"),
                (3, "premium@appforge.com", "hash", "Member", "premium")
            ]
            try:
                cursor.executemany(
                    "INSERT INTO users (id, email, password_hash, role, subscription) VALUES (?, ?, ?, ?, ?);",
                    users_data
                )
            except Exception:
                # Fallback if structure varies slightly
                pass

        if "contacts" in tables:
            contacts_data = [
                (1, "Alice Smith", "alice@example.com", "123-456", "Tech Corp", 2),
                (2, "Bob Jones", "bob@example.com", "456-789", "Health Inc", 2),
                (3, "Charlie Brown", "charlie@example.com", "789-012", "Edu Group", 3)
            ]
            try:
                cursor.executemany(
                    "INSERT INTO contacts (id, name, email, phone, company, owner_id) VALUES (?, ?, ?, ?, ?, ?);",
                    contacts_data
                )
            except Exception:
                pass

        if "deals" in tables:
            deals_data = [
                (1, "Enterprise License Sale", 15000.00, "Prospecting", 1),
                (2, "Mid-Market Growth Plan", 5000.00, "Negotiation", 2),
                (3, "SaaS Annual Agreement", 1200.00, "Closed Won", 3)
            ]
            try:
                cursor.executemany(
                    "INSERT INTO deals (id, title, amount, stage, contact_id) VALUES (?, ?, ?, ?, ?);",
                    deals_data
                )
            except Exception:
                pass
                
        self.conn.commit()

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute(self, sql: str, params: tuple = ()) -> Tuple[int, int]:
        """Executes INSERT, UPDATE, DELETE queries. Returns (lastrowid, rowcount)."""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor.lastrowid, cursor.rowcount

    def close(self):
        self.conn.close()
