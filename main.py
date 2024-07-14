from typing import List, Dict
from fastapi import FastAPI
from modules.MachineLearningModel import MachineLearningModel

app = FastAPI()
movie_recommender = MachineLearningModel()
print('only an index')


@app.get("/", response_model=Dict)
def index():
    # recommendations = movie_recommender.get_recommendations(movie_title)
    # return {"recommendations": recommendations}
    return {"items": {"name": "Hammer", "category": "Tool"}}


@app.get("/recommendation/{movie_title}", response_model=Dict)
def get_recommendation(movie_title: str):
    recommendations = movie_recommender.get_recommendations(movie_title)
    return {"movie_title": movie_title, "recommendations": recommendations}

# @app.get("/recommendation/{movie_title}", response_model=List[str])
# def get_recommendation(movie_title: str):
#     print("the passed movie title was:",movie_title)
#     recommendations = movie_recommender.get_recommendations(movie_title)
#     return {"recommendations": recommendations}


# print(get_recommendation("Spider-Man"))
