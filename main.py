from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.TrainingModule import TrainingModule
from modules.MachineLearningModel import MachineLearningModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8002",
    "http://127.0.0.1:8002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


app.mount("/static", StaticFiles(directory="www"), name="static")
app.mount("/assets", StaticFiles(directory="www/assets"), name="assets")


training_module = TrainingModule()
training_module.train_model()

movie_recommender = MachineLearningModel(
    training_module.load_training_data(), training_module.load_similarity_scores_data()
)


@app.get("/")
def index():
    return FileResponse("www/index.html")


@app.get("/recommendation/{movie_title}", response_model=Dict)
def get_recommendation(movie_title: str):
    recommendations = movie_recommender.get_recommendations(movie_title)
    return {"movie_title": movie_title, "recommendations": recommendations}


@app.get("/get-movie-titles", response_model=Dict)
def get_movie_titles():
    titles = movie_recommender.get_movie_titles()
    print(type(titles))
    return {"movie_titles": movie_recommender.get_movie_titles()}


@app.get("/dump-data", response_model=Dict)
def dump_data():
    return movie_recommender.dump_data()
