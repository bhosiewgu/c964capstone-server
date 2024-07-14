from typing import Dict
from fastapi import FastAPI
from modules.TrainingModule import TrainingModule
from modules.MachineLearningModel import MachineLearningModel

app = FastAPI()
training_module = TrainingModule()
training_module.train_model()

movie_recommender = MachineLearningModel(
    training_module.load_training_data(), training_module.load_similarity_scores_data()
)


@app.get("/", response_model=Dict)
def index():
    # recommendations = movie_recommender.get_recommendations(movie_title)
    # return {"recommendations": recommendations}
    return {"items": {"name": "Hammer", "category": "Tool"}}


@app.get("/recommendation/{movie_title}", response_model=Dict)
def get_recommendation(movie_title: str):
    recommendations = movie_recommender.get_recommendations(movie_title)
    return {"movie_title": movie_title, "recommendations": recommendations}
