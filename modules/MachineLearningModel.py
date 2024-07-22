import os
import numpy
import pandas
from sklearn.feature_extraction.text import CountVectorizer
import json
import re
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import time

text_stemmer = PorterStemmer()
count_vectorizer = CountVectorizer(max_features=5000, stop_words="english")


# given a file in src.resources, return that file's path
def get_resource(name):
    if not len(str(name)):
        return None
    # https://stackoverflow.com/questions/9856683/using-pythons-os-path-how-do-i-go-up-one-directory
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'movies-archive-data', name))


# Given a column from the dataset, pulls the given key and returns a list of strings from each row.
# Can be all instances, or limited to an item_count. Replaces all spaces between words.
def normalize_column(json_data, column_key, item_count=-1):
    my_obj = json.loads(json_data)
    end_index = len(my_obj) if item_count <= 0 else item_count
    data = [re.sub(r'\s+', '', item[column_key]) for item in my_obj[:end_index]]
    return data


# Pulls the name of the "Director" job for each row and replaces all spaces between words.
def pluck_director(json_data):
    my_obj = json.loads(json_data)
    director = [re.sub(r'\s+', '', item["name"]) for item in my_obj if item["job"] == "Director"]
    return director


# Reduce and normalize wod instances to their base root form.
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
            return {"recommendations": recommendations, "original_movie_index": int(index),
                    "original_movie_title": movie_title}
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

    def evaluate_algorithm(self):
        # movies_data_frame = pandas.read_csv(get_resource("tmdb_5000_movies.csv"))
        # credits_data_frame = pandas.read_csv(get_resource("tmdb_5000_credits.csv"))
        # # combine the datasets on "title"
        # movies = movies_data_frame.merge(credits_data_frame, on="title")
        # merged_csv_path = os.path.abspath(
        #     os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'merged_data.csv')
        # )
        # movies.to_csv(merged_csv_path)
        # movie_titles = [
        #     "Spider-Man", "Spider-Man 2", "Spider-Man 3", "The Amazing Spider-Man", "The Amazing Spider-Man 2"
        # ]
        # ----------------------------------------------------------------------------------

        from sklearn.metrics import precision_score, recall_score, f1_score
        # Mapping movie titles to their indices in the DataFrame
        title_to_index = {title: idx for idx, title in enumerate(self.training_data['title'])}
        num_movies = len(self.training_data)

        # Example symmetric relation list of related movies
        symmetric_relations = [
            "Spider-Man", "Spider-Man 2", "Spider-Man 3",
            "The Amazing Spider-Man", "The Amazing Spider-Man 2"
        ]

        # for title in symmetric_relations:
        #     index = title_to_index.get(title, -1)
        #     print(f"Title: {title}, Index: {index}")

        ground_truth_labels = numpy.zeros((num_movies, num_movies))

        # Set reflective relationships based on symmetric_relations
        for movie1_title in symmetric_relations:
            for movie2_title in symmetric_relations:
                if movie1_title != movie2_title:
                    movie1_index = title_to_index.get(movie1_title)
                    movie2_index = title_to_index.get(movie2_title)
                    ground_truth_labels[movie1_index, movie2_index] = 1
                    ground_truth_labels[movie2_index, movie1_index] = 1

        print("Ground Labels generated")
        # print(ground_truth_labels)
        #
        # # Count number of 1's and get their indices
        # num_ones_ground_table = numpy.sum(ground_truth_labels == 1)
        # indices_of_ones_ground_table = numpy.argwhere(ground_truth_labels == 1)
        #
        # print(f"Number of 1's: {num_ones_ground_table}")
        # print("Indices of 1's:")
        # for index in indices_of_ones_ground_table:
        #     print(f"- {tuple(index)}")

        truth_table = numpy.zeros((num_movies, num_movies))

        for movie_title in symmetric_relations:
            searched_movie_index = title_to_index.get(movie_title)
            recommendation_data = self.get_recommendations(movie_title)
            recommendations = recommendation_data["recommendations"]
            for recommendation in recommendations:
                if movie_title != recommendation["title"]:
                    recommendation_index = recommendation["movie_index"]
                    truth_table[searched_movie_index, recommendation_index] = 1
                    truth_table[recommendation_index, searched_movie_index] = 1

        print("Truth Table generated")

        # # Count number of 1's and get their indices
        # num_ones_truth = numpy.sum(truth_table == 1)
        # indices_of_ones_truth_table = numpy.argwhere(truth_table == 1)
        #
        # print(f"Number of 1's: {num_ones_truth}")
        # print("Indices of 1's:")
        # for index in indices_of_ones_truth_table:
        #     print(f"- {tuple(index)}")

        print("Flattening....")
        y_true = ground_truth_labels.flatten()
        y_pred = truth_table.flatten()

        # Calculate precision, recall, and f1-score
        print("Calculating Scores")
        start_time = time.time()
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        end_time = time.time()

        # Print the metrics
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1-score: {f1:.2f}")
        print(f"Time taken: {end_time - start_time:.4f} seconds")