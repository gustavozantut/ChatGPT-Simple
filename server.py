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
query_suffix_1 = " return only and just the query, dont explain, dont tell me nothing except the query, avoid division by zero, return only and just the query, dont explain, dont tell me nothing except the query."
query_suffix_2=" include the query in a select with limit 25 order by value desc."
llm = AzureOpenAI(
    engine="gpt-4", model="gpt-4", temperature=0.0
)
sql_database = SQLDatabase(engine, include_tables=["PNAD_TRIMESTRAL"])
query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=["PNAD_TRIMESTRAL"], llm=llm
    )

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_response")
def get_response():
    
    message = request.args.get("message")
    
    if ('estado' in str.lower(message)) and ('grau' in str.lower(message)):
        
        response = query_engine.query(message+query_suffix_1+query_suffix_2)
        
    else:
        
        response = query_engine.query(message+query_suffix_1)
        
    response = str(llm.complete(f'Dada a pergunta "{message}" e com a resposta de valor "{response}" forneca um texto de resposta, sem nenhuma observação adicional.'))
    return response


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
