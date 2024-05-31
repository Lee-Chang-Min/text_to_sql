import json
import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import debugpy

import prompt_Strategy

debugpy.listen(("0.0.0.0", 8501))

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


@app.get('/')
def health():
    print("hello")
    return {
        "message": "OK 🚀"
    }
    

# @app.get("/", response_class=HTMLResponse)
# async def get_form(request: Request):
#     print("request:", request)
#     return templates.TemplateResponse("front.html", {"request": request})

# @app.post("/sql", response_class=HTMLResponse)
# async def search(request: Request, question: str = Form(...)):
#     if not question:
#         return {"error": "question is required"}
#     print('화면의 question 입력:', question)
    
#     answer = prompt_Strategy.main(question)
#     return templates.TemplateResponse("front.html", {"request": request, "answer": answer})
    
