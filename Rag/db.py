import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class SupabaseDB:

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL not set!")

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    @contextmanager
    def get_cursor(self):
        conn = self.get_connection()

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                yield cursor
                conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    def get_or_create_farmer(self, phone_number: str) -> str:

        with self.get_cursor() as cur:

            cur.execute(
                """
                SELECT id
                FROM farmers
                WHERE phone_number = %s
                """,
                (phone_number,)
            )

            row = cur.fetchone()

            if row:
                farmer_id = row["id"]

                cur.execute(
                    """
                    UPDATE farmers
                    SET last_active_at = now()
                    WHERE id = %s
                    """,
                    (farmer_id,)
                )

                return farmer_id

            cur.execute(
                """
                INSERT INTO farmers (phone_number)
                VALUES (%s)
                RETURNING id
                """,
                (phone_number,)
            )

            return cur.fetchone()["id"]

    def log_conversation(self, farmer_id: str, state: dict) -> str:

        with self.get_cursor() as cur:

            cur.execute(
                """
                INSERT INTO conversations
                    (
                        farmer_id,
                        question,
                        crop,
                        disease,
                        observations,
                        confidence,
                        needs_retrieval,
                        diagnosis_uncertain,
                        answer
                    )
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    farmer_id,
                    state.get("question"),
                    state.get("crop"),
                    state.get("disease"),
                    state.get("observations"),
                    state.get("confidence"),
                    state.get("needs_retrieval"),
                    state.get("diagnosis_uncertain"),
                    state.get("answer"),
                )
            )

            return cur.fetchone()["id"]

    def get_recent_conversations(
        self,
        farmer_id: str,
        limit: int = 5
    ) -> list:

        with self.get_cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM conversations
                WHERE farmer_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (farmer_id, limit)
            )

            return cur.fetchall()

    def close(self):
        pass