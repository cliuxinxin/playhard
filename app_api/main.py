from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

class Activity(BaseModel):
    title: str
    city: str
    start_time: str
    end_time: str
    age_range: str
    tags: List[str]

@app.get("/activities", response_model=List[Activity])
def get_activities():
    with open("../data/raw/sjpl.json", "r") as f:
        data = json.load(f)
    return [
        {
            "title": item["title"],
            "city": "San Jose",
            "start_time": "2025-06-15 10:30",
            "end_time": "2025-06-15 11:00",
            "age_range": "1-3",
            "tags": ["storytime", "free"]
        } for item in data
    ]