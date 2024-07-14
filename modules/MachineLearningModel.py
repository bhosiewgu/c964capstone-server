import os
import pandas
from sklearn.naive_bayes import MultinomialNB
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


# def dump_pickle_object(obj, name):
#     path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts', name))
#     pickle.dump(obj, open(path, 'wb'))


def normalize_column(json_data, column_key, item_count=-1):
    my_obj = json.loads(json_data)
    end_index = len(my_obj) if item_count <= 0 else item_count
    # data = [item[column_key] for item in my_obj[:end_index]]
    data = [re.sub(r'\s+', '', item[column_key]) for item in my_obj[:end_index]]
    return data


def pluck_director(json_data):
    my_obj = json.loads(json_data)
    director = [item["name"] for item in my_obj if item["job"] == "Director"]
    # director = [re.sub(r'\s+', '', item["name"]) for item in my_obj if item["job"] == "Director"]
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
    movies["overview"] = movies["overview"].apply(lambda str: str.split())
    movies["tags"] = movies["overview"] + movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + \
                     movies["crew"]

    # print(movies.loc[0, 'genres'])
    # print(movies.loc[0, 'keywords'])
    # print(movies.loc[0, 'cast'])
    # print(movies.loc[0, 'crew'])
    # print(movies.loc[0, 'overview'])
    # print(movies.loc[0, 'tags'])

    training_data = movies[["movie_id", "title", "tags"]]
    training_data["tags"] = training_data["tags"].apply(lambda str_text: " ".join(str_text))
    training_data["tags"] = training_data["tags"].apply(lambda str_text: str_text.lower())
    training_data["tags"] = training_data["tags"].apply(stem_text)

    print(training_data.loc[0], "movie_id")
    print(training_data.loc[0], "title")
    print(training_data.loc[0], "tags")

    similarity_vectors = count_vectorizer.fit_transform(training_data["tags"]).toarray()
    similarity_scores = cosine_similarity(similarity_vectors)

    # dump_pickle_object(training_data, "movie_list.pkl")
    # dump_pickle_object(similarity_scores, "similarity_scores.pkl")
    return {"similarity_scores": similarity_scores, "training_data": training_data}


class MachineLearningModel:
    def __init__(self, training_data=None, similarity_scores=None):
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
            recommendations = [self.training_data.iloc[i[0]].title for i in distances[1:6]]
            return recommendations
        except IndexError:
            return []

    def dump_data(self):
        return {"training_data": self.training_data.to_json(orient='records')}

    def pickle_data(self):
        training_data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'training_data.pkl')
        )
        pickle.dump(self.training_data, open(training_data_path, 'wb'))
        similarity_score_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'similarity_scores.pkl')
        )
        pickle.dump(self.similarity_scores, open(similarity_score_path, 'wb'))

    # # Alternative method using a regular loop
    # def get_recommendations_alternative(self, movie_title):
    #     index = self.training_data[self.training_data["title"] == movie_title].index[0]
    #     distances = sorted(list(enumerate(self.similarity_scores[index])), reverse=True, key=lambda x: x[1])
    #
    #     recommendations = []
    #     for i in distances[1:6]:
    #         recommendations.append(self.training_data.iloc[i[0]].title)
    #     return recommendations
