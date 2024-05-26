import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from controller import connect_to_bigquery 
import prompt_Strategy

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

@app.get("/search")
async def search():
    
    # outcome = Controller.
    # print(f"result {outcome}")

    # response = {
    #     "result": outcome
    # }

    connect_to_bigquery()
    
@app.get("/sql")
def search():
    # prompt_Strategy.connet_db()
    prompt_Strategy.main()
    
