import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlController import SqlController

app = FastAPI()

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Production env.
prod = False


@app.get('/')
def health():
    print("hello")

    result = SqlController(prod)

    답변 = result.response("고유 사용자 수를 알려줘")
    print(답변)
    return {
        "message": "OK 🚀"
    }
    
