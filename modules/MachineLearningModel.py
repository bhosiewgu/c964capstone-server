import os
import pandas
from sklearn.feature_extraction.text import CountVectorizer
import json
import re
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

text_stemmer = PorterStemmer()
count_vectorizer = CountVectorizer(max_features=5000, stop_words="english")


# given a file in src.resources, return that file's path
def get_resource(name):
    if not len(str(name)):
        return None
    # https://stackoverflow.com/questions/9856683/using-pythons-os-path-how-do-i-go-up-one-directory
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'movies-archive-data', name))


def normalize_column(json_data, column_key, item_count=-1):
    my_obj = json.loads(json_data)
    end_index = len(my_obj) if item_count <= 0 else item_count
    # data = [item[column_key] for item in my_obj[:end_index]]
    data = [re.sub(r'\s+', '', item[column_key]) for item in my_obj[:end_index]]
    return data


def pluck_director(json_data):
    my_obj = json.loads(json_data)
    # director = [item["name"] for item in my_obj if item["job"] == "Director"]
    director = [re.sub(r'\s+', '', item["name"]) for item in my_obj if item["job"] == "Director"]
    return director


def stem_text(text):
    return " ".join(map(text_stemmer.stem, text.split()))


def load_machine_learning_data():
    # load the csv files
    movies_data_frame = pandas.read_csv(get_resource("tmdb_5000_movies.csv"))
    credits_data_frame = pandas.read_csv(get_resource("tmdb_5000_credits.csv"))
    # combine the datasets on "title"
    movies = movies_data_frame.merge(credits_data_frame, on="title")
    # use these columns
    movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
    # remove duplicates
    movies.dropna(inplace=True)
    # normalize these objects from objects to lists of plucked values
    movies["genres"] = movies["genres"].apply(lambda json_data: normalize_column(json_data, "name"))
    movies["keywords"] = movies["keywords"].apply(lambda json_data: normalize_column(json_data, "name"))
    movies["cast"] = movies["cast"].apply(lambda json_data: normalize_column(json_data, "name", 3))
    movies["crew"] = movies["crew"].apply(pluck_director)
    movies["overview"] = movies["overview"].apply(lambda str_data: str_data.split())

    # classify the data
    training_data = movies[["movie_id", "title"]]
    training_data["stemmed"] = (
            movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + movies["crew"]
    ).apply(lambda str_text: " ".join(str_text).lower())
    training_data["stemmed"] = training_data["stemmed"].apply(stem_text)
    similarity_vectors = count_vectorizer.fit_transform(training_data["stemmed"]).toarray()
    similarity_scores = cosine_similarity(similarity_vectors)

    return {"similarity_scores": similarity_scores, "training_data": training_data}


class MachineLearningModel:
    def __init__(self, training_data=None, similarity_scores=None):
        # no need to train
        if training_data is not None and similarity_scores is not None:
            self.training_data = training_data
            self.similarity_scores = similarity_scores
        else:
            training_model = load_machine_learning_data()
            self.training_data = training_model["training_data"]
            self.similarity_scores = training_model["similarity_scores"]

    def get_recommendations(self, movie_title):
        try:
            index = self.training_data[self.training_data["title"] == movie_title].index[0]
            distances = sorted(list(enumerate(self.similarity_scores[index])), reverse=True, key=lambda x: x[1])

            # Using list comprehension to collect recommendations
            recommendations = [
                {
                    'movie_index': int(i[0]),
                    'title': self.training_data.iloc[i[0]]['title'],
                    'movie_id': int(self.training_data.iloc[i[0]]['movie_id'])
                }
                for i in distances[1:6]
            ]
            return {"recommendations": recommendations, "original_movie_index": int(index), "original_movie_title": movie_title}
        except IndexError:
            return []

    def get_movie_titles(self):
        return self.training_data["title"].values.tolist()

    def pickle_data(self):
        training_data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'training_data.pkl')
        )
        pickle.dump(self.training_data, open(training_data_path, 'wb'))
        similarity_score_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'similarity_scores.pkl')
        )
        pickle.dump(self.similarity_scores, open(similarity_score_path, 'wb'))
