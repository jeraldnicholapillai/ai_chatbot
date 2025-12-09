import streamlit as st
import pandas as pd
import sqlite3
from openai import AzureOpenAI

# -----------------------------
# Azure OpenAI Settings
# -----------------------------
client = AzureOpenAI(
    api_key="EZvsLgoMjONIsOjWpZSJj8SVY8DqLtPOktVITBEsG3eyyvxG5kj6JQQJ99BLACF24PCXJ3w3AAAAACOGbtrJ",
    azure_endpoint="https://llmeng.openai.azure.com/",
    api_version="2024-02-15-preview"
)

chat_model = "gpt-4.1-mini"

# -----------------------------
# Load Database Schema
# -----------------------------
with open("schema.txt", "r") as f:
    DB_SCHEMA = f.read()

# -----------------------------
# Convert NL → SQL
# -----------------------------
def generate_sql(question):
    prompt = f"""
You are an expert SQL generator. 
Convert the question into a valid SQL query.
Only return SQL. No explanation.

DATABASE SCHEMA:
{DB_SCHEMA}

QUESTION:
{question}

SQL:
"""

    response = client.chat.completions.create(
        model=chat_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    sql = response.choices[0].message.content.strip()

    # --------------- FIX ---------------
    sql = sql.replace("```sql", "").replace("```", "").strip()
    if sql.lower().startswith("sql "):
        sql = sql[4:].strip()
    # -----------------------------------

    return sql
    #return response.choices[0].message.content.strip()

# -----------------------------
# Execute SQL Query
# -----------------------------
def run_sql(sql):
    conn = sqlite3.connect("db.sqlite3")
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        return f"SQL Error: {str(e)}"
    finally:
        conn.close()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="NL → SQL App", layout="centered")
st.title("🧠 Natural Language → SQL Query Generator")
st.write("Enter a question and the system will generate and execute an SQL query.")

question = st.text_input("Ask a question:", placeholder="e.g., Show total sales by region")

if st.button("Generate SQL"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL using GPT-4.1-mini..."):
            sql_query = generate_sql(question)

        st.code(sql_query, language="sql")

        with st.spinner("Running SQL query..."):
            result = run_sql(sql_query)

        if isinstance(result, pd.DataFrame):
            st.success("Here are the results:")
            st.dataframe(result, use_container_width=True)

            # Optional chart if numeric column exists
            numeric_cols = result.select_dtypes(include=['float', 'int']).columns
            if len(numeric_cols) > 0:
                st.write("📊 Visualization")
                st.bar_chart(result[numeric_cols], use_container_width=True)
        else:
            st.error(result)
