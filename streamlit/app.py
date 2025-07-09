import streamlit as st
import pandas as pd
from backend.src.support_systems.match_maker.prompt_generation import PromptGeneration
from backend.src.support_systems.match_maker.image_pipeline import ImagePipeline
from backend.src.support_systems.match_maker.visualization import visualize_recommendations
from backend.src.support_systems.match_maker.image_store import ImageStore

data = {
    "StudentID": ["OIRK91JPG", "Q5U0D1GVS"],
    "Extrovert": [1, 4], "Introvert": [4, 1],
    "Sensing": [1, 5], "Intuitive": [4, 0],
    "Thinking": [2, 1], "Feeling": [3, 4],
    "Judging": [1, 3], "Perceiving": [4, 2],
    "Active": [3, 8], "Reflective": [8, 3],
    "Sensing_FSLSM": [2, 7], "Intuitive_FSLSM": [9, 4],
    "Visual": [9, 3], "Verbal": [2, 8],
    "Sequential": [3, 7], "Global": [8, 4],
    "Text_Time": [633, 741]
}

prompt_gen = PromptGeneration()
df, prompts = prompt_gen.process_responses(data)

image_pipeline = ImagePipeline()
image_pipeline.generate_and_store_images(prompts)
recommendations = image_pipeline.cluster_and_recommend(df)

image_store = ImageStore()
visualize_recommendations(df, recommendations, image_store)
