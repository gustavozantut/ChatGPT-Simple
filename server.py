import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sqlalchemy.engine import URL
from sqlalchemy import (
    create_engine,
    MetaData
)
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase
from llama_index.llms.azure_openai import AzureOpenAI

load_dotenv()  # load env vars from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
server = os.getenv("server")
database = os.getenv("database")
username = os.getenv("username")
password = os.getenv("password")
driver = '{ODBC Driver 18 for SQL Server}'
# Connect to the SQL Server database
conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes'
connection_url = URL.create(
    "mssql+pyodbc", 
    query={"odbc_connect": conn_str}
)
engine = create_engine(connection_url)
metadata_obj = MetaData()
query_suffix = "return only and just the query, dont explain, dont tell me nothing except the query"
llm = AzureOpenAI(
    engine="gpt-4", model="gpt-4", temperature=0.0
)
sql_database = SQLDatabase(engine, include_tables=["pnad"])
query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=["pnad"], llm=llm
    )

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_response")
def get_response():
    
    message = request.args.get("message")
    response = str(query_engine.query(f'Dada a pergunta "{message}" e com a resposta de valor "{query_engine.query(message+query_suffix)}" forneca um texto de resposta, sem nenhuma observação adicional.'))
    return response


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
