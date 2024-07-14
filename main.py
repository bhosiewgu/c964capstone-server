from typing import List, Dict
from fastapi import FastAPI
from train_model import TrainingModel
from modules.MachineLearningModel import MachineLearningModel

app = FastAPI()
training_model = TrainingModel()
training_model.train_model()

movie_recommender = MachineLearningModel(training_model.load_training_data(), training_model.load_similarity_scores_data())


@app.get("/", response_model=Dict)
def index():
    # recommendations = movie_recommender.get_recommendations(movie_title)
    # return {"recommendations": recommendations}
    return {"items": {"name": "Hammer", "category": "Tool"}}


@app.get("/recommendation/{movie_title}", response_model=Dict)
def get_recommendation(movie_title: str):
    recommendations = movie_recommender.get_recommendations(movie_title)
    return {"movie_title": movie_title, "recommendations": recommendations}
