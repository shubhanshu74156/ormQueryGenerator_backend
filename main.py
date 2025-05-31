import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

import config

SECRET_KEY = os.getenv("OPENAPI_KEY")

client = OpenAI(api_key=SECRET_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    sql_schema: str
    orm: str
    language: str
    question: str


@app.post("/convert")
def convert_sql(req: QueryRequest):
    prompt = f"""
{req.sql_schema}

Write the {req.orm} ORM query only for {req.question}.
Do not explain. Return only valid {req.language} code using {req.orm} ORM.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return {"result": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
