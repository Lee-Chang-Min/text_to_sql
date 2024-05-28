import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.agent import connect_to_bigquery 
import prompt_Strategy

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/sqlagent")
async def search():

    connect_to_bigquery()
    

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    print("request:", request)
    return templates.TemplateResponse("front.html", {"request": request})

@app.post("/sql", response_class=HTMLResponse)
async def search(request: Request, question: str = Form(...)):
    if not question:
        return {"error": "question is required"}
    print('화면의 question 입력:', question)
    
    answer = prompt_Strategy.main(question)
    return templates.TemplateResponse("front.html", {"request": request, "answer": answer})
    
# @app.post("/sql", response_class=HTMLResponse)
# async def search(request: Request):
#     data = await request.json()
#     print(data)
    # prompt_Strategy.connet_db()
    # prompt_Strategy.main()
    # return templates.TemplateResponse("form.html", {"request": request, "answer": answer, "question": question, "chat_history": chat_history})
    
# app.mount("/static", StaticFiles(directory="static"), name="static")