from fastapi import APIRouter, HTTPException
from google.cloud import bigquery
from langchain.sql_database import SQLDatabase

import constant as env

def get_db() -> SQLDatabase:
    client = bigquery.Client()
    return SQLDatabase.from_uri(f"bigquery://{client.project}")

