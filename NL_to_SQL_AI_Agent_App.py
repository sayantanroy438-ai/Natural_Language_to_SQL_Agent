import os

import pandas as pd
import streamlit as st
import mysql.connector

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CONFIGURATION HELPER
# Works with both:
# Local VS Code -> .env
# Streamlit Cloud -> Secrets
# =========================================================

def get_config(key, default=None):

    try:
        value = st.secrets.get(key)
    except Exception:
        value = None

    return value or os.getenv(key, default)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NL to SQL AI Agent",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
        color: #ffffff;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #aab2c0;
        margin-bottom: 35px;
    }

    /* Section headings */
    .section-title {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Info cards */
    .info-card {
        background-color: #161b22;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
    }

    .info-number {
        font-size: 26px;
        font-weight: 700;
        color: #58a6ff;
    }

    .info-label {
        font-size: 14px;
        color: #8b949e;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6e7681;
        font-size: 13px;
        margin-top: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🤖 Natural Language to SQL AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions in plain English and let Gemini generate the SQL query.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=get_config("GEMINI_API_KEY")
)


# =========================================================
# MYSQL CONNECTION
# =========================================================

def connect_to_sql():

    return mysql.connector.connect(
        host=get_config("MYSQL_HOST"),
        user=get_config("MYSQL_USER"),
        password=get_config("MYSQL_PASSWORD"),
        database=get_config("MYSQL_DATABASE"),
        port=int(get_config("MYSQL_PORT", 3306))
    )


# =========================================================
# DATABASE SCHEMA
# =========================================================

schema = """
TABLE: bridge
COLUMNS:
bp INT
Class TEXT
FullName TEXT
ID INT
Sex TEXT


TABLE: chess
COLUMNS:
cp INT
Class TEXT
FullName TEXT
ID INT
Sex TEXT


TABLE: music
COLUMNS:
ID INT
Type TEXT


TABLE: student
COLUMNS:
Class TEXT
DCode TEXT
DOB TEXT
FullName TEXT
HCode TEXT
ID INT
MTest INT
newdob DATE
PTest INT
Remission INT
Sex TEXT
"""


# =========================================================
# GENERATE SQL USING GEMINI
# =========================================================

def generate_sql_query(question):

    prompt = f"""
You are an expert MySQL SQL generator.

Convert the user's natural language question
into a valid MySQL SQL query.

Use ONLY the tables and columns provided below.

DATABASE SCHEMA:
{schema}

RULES:
1. Return ONLY the SQL query.
2. Do not provide explanations.
3. Do not use markdown code fences.
4. Do not invent table names.
5. Do not invent column names.
6. Use valid MySQL syntax.

USER QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text.strip()


# =========================================================
# USER QUESTION
# =========================================================

st.markdown(
    '<div class="section-title">💬 Ask Your Question</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "",
    placeholder="Example: Show the list of Female students",
    label_visibility="collapsed"
)


# =========================================================
# BUTTON
# =========================================================

generate_button = st.button(
    "✨ Generate SQL & Run Query",
    use_container_width=True
)


# =========================================================
# MAIN PROCESS
# =========================================================

if generate_button:

    if not question:

        st.warning("⚠️ Please enter a question first.")

    else:

        try:

            # -------------------------------------------------
            # Generate SQL
            # -------------------------------------------------

            with st.spinner("🧠 Gemini is generating your SQL query..."):

                sql_query = generate_sql_query(question)


            # -------------------------------------------------
            # SQL SECTION
            # -------------------------------------------------

            st.markdown(
                '<div class="section-title">🧠 Generated SQL</div>',
                unsafe_allow_html=True
            )

            st.code(
                sql_query,
                language="sql"
            )


            # -------------------------------------------------
            # DATABASE CONNECTION
            # -------------------------------------------------

            with st.spinner("🔗 Connecting to MySQL database..."):

                conn = connect_to_sql()

                cursor = conn.cursor()


            # -------------------------------------------------
            # EXECUTE QUERY
            # -------------------------------------------------

            with st.spinner("⚡ Executing SQL query..."):

                cursor.execute(sql_query)

                results = cursor.fetchall()


            # -------------------------------------------------
            # CREATE DATAFRAME
            # -------------------------------------------------

            columns = [
                column[0]
                for column in cursor.description
            ]

            df = pd.DataFrame(
                results,
                columns=columns
            )


            # -------------------------------------------------
            # RESULT SUMMARY
            # -------------------------------------------------

            st.markdown(
                '<div class="section-title">📊 Query Results</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"""
                    <div class="info-card">
                        <div class="info-number">{len(df)}</div>
                        <div class="info-label">Rows Returned</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:

                st.markdown(
                    f"""
                    <div class="info-card">
                        <div class="info-number">{len(df.columns)}</div>
                        <div class="info-label">Columns</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.write("")


            # -------------------------------------------------
            # DATAFRAME
            # -------------------------------------------------

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


            # -------------------------------------------------
            # CLOSE DATABASE CONNECTION
            # -------------------------------------------------

            cursor.close()
            conn.close()


        except Exception as e:

            st.error(
                f"❌ Something went wrong: {e}"
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Built with ❤️ using Streamlit, Gemini AI & MySQL
    </div>
    """,
    unsafe_allow_html=True
)
