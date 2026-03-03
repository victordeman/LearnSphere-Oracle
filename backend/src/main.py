from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from src.support_systems.match_maker.prompt_generation import PromptGeneration
from src.support_systems.match_maker.image_pipeline import ImagePipeline

app = FastAPI()
prompt_gen = PromptGeneration()
image_pipeline = ImagePipeline()

class SurveyResponse(BaseModel):
    StudentID: str
    Extrovert: int
    Introvert: int
    Sensing: int
    Intuitive: int
    Thinking: int
    Feeling: int
    Judging: int
    Perceiving: int
    Active: int
    Reflective: int
    Sensing_FSLSM: int
    Intuitive_FSLSM: int
    Visual: int
    Verbal: int
    Sequential: int
    Global: int
    Text_Time: int

class MatchRequest(BaseModel):
    survey_data: List[SurveyResponse]

@app.post("/match")
async def get_matches(request: MatchRequest):
    try:
        data = [item.model_dump() for item in request.survey_data]
        df, prompts = prompt_gen.process_responses(data)
        recommendations = image_pipeline.cluster_and_recommend(df)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
