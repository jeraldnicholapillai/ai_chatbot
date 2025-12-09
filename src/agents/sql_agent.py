from openai import AzureOpenAI
import sqlite3

class SQLAgent:
    def __init__(self, model, client):
        self.model = model
        self.client = client

    def generate_sql(self, question, schema):
        prompt = f"""
        You are a SQL expert agent.
        Convert the user question into SQL ONLY.

        SCHEMA:
        {schema}

        QUESTION:
        {question}

        SQL:
        """

        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return res.choices[0].message.content.strip()

    def run_sql(self, sql):
        try:
            conn = sqlite3.connect("db.sqlite3")
            df = pd.read_sql_query(sql, conn)
            return df
        except Exception as e:
            return f"SQL Error: {str(e)}"
        finally:
            conn.close()
