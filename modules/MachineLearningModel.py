import os
import numpy
import pandas
import json
import re
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle
import time

text_stemmer = PorterStemmer()
tfid_vectorizer = TfidfVectorizer(stop_words='english')


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
    movies.drop_duplicates(subset=['movie_id'], keep='first', inplace=True)
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

    tfid_matrix = tfid_vectorizer.fit_transform(training_data["stemmed"]).toarray()
    nn = NearestNeighbors(n_neighbors=6, metric='cosine')
    nn.fit(tfid_matrix)

    return {"nearest_neighbors": nn, "tfid_matrix": tfid_matrix, "training_data": training_data}


class MachineLearningModel:
    def __init__(self, training_data=None, nearest_neighbors=None, tfid_matrix=None):
        # no need to train
        if training_data is not None and nearest_neighbors is not None and tfid_matrix is not None:
            self.training_data = training_data
            self.nearest_neighbors = nearest_neighbors
            self.tfid_matrix = tfid_matrix
        else:
            training_model = load_machine_learning_data()
            self.training_data = training_model["training_data"]
            self.nearest_neighbors = training_model["nearest_neighbors"]
            self.tfid_matrix = training_model["tfid_matrix"]

    def get_recommendations(self, movie_title):
        try:
            index = self.training_data[self.training_data['title'] == movie_title].index[0]
            query_vector = numpy.array([self.tfid_matrix[index]])
            distances, indices = self.nearest_neighbors.kneighbors(query_vector)

            # Using list comprehension to collect recommendations
            recommendations = [
                {
                    'movie_index': int(self.training_data.iloc[i]['movie_id']),
                    # Assuming 'movie_id' is the column name
                    'title': self.training_data.iloc[i]['title'],
                    'movie_id': int(self.training_data.iloc[i]['movie_id'])
                }
                for i in indices[0][1:6]  # Exclude the first index (itself) and take the top 5 recommendations
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
        nearest_neighbors_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'nearest_neighbors.pkl')
        )
        pickle.dump(self.nearest_neighbors, open(nearest_neighbors_path, 'wb'))
        tfid_matrix_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'tfid_matrix.pkl')
        )
        pickle.dump(self.tfid_matrix, open(tfid_matrix_path, 'wb'))

    def evaluate_algorithm(self):
        # # This script gives me a merged CSV to look at
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
        ground_truth_labels = numpy.zeros((num_movies, num_movies))
        truth_table_predictions = numpy.zeros((num_movies, num_movies))

        # These groups are expected to be mutually exclusive for when the top 5 recommendations come back
        symmetric_relations = [
            [
                "Spider-Man", "Spider-Man 2", "Spider-Man 3",
                "The Amazing Spider-Man", "The Amazing Spider-Man 2"
            ],
            [
                "Batman", "The Dark Knight", "The Dark Knight Rises", "Batman: The Dark Knight Returns, Part 2",
                "Batman Begins", "Batman & Robin", "Batman Forever", "Batman Returns"
            ],
            [
                "Pirates of the Caribbean: Dead Man's Chest", "Pirates of the Caribbean: On Stranger Tides",
                "Pirates of the Caribbean: The Curse of the Black Pearl", "Pirates of the Caribbean: At World's End"
            ],
            [
                "Star Trek III: The Search for Spock", "Star Trek II: The Wrath of Khan", "Star Trek: First Contact",
                "Star Trek: Generations", "Star Trek: The Motion Picture", "Star Trek V: The Final Frontier",
                "Star Trek VI: The Undiscovered Country", "Star Trek IV: The Voyage Home", "Star Trek Into Darkness",
                "Star Trek: Insurrection", "Star Trek: Nemesis", "Star Trek Beyond", "Star Trek"
            ],
            [
                "GoldenEye", "The World Is Not Enough", "Die Another Day", "Tomorrow Never Dies", "Moonraker",
                "A View to a Kill", "For Your Eyes Only", "Octopussy", "The Spy Who Loved Me", "Live and Let Die",
                "The Man with the Golden Gun", "Goldfinger", "From Russia with Love", "Dr. No", "Never Say Never Again",
                "You Only Live Twice", "Thunderball", "Diamonds Are Forever", "Spectre", "Quantum of Solace", "Skyfall",
                "Casino Royale", "Licence to Kill", "The Living Daylights", "On Her Majesty's Secret Service"
            ]
        ]

        for symmetric_group in symmetric_relations:
            for i in range(len(symmetric_group)):
                for j in range(i + 1, len(symmetric_group)):
                    movie1_index = title_to_index[symmetric_group[i]]
                    movie2_index = title_to_index[symmetric_group[j]]
                    ground_truth_labels[movie1_index, movie2_index] = 1
                    ground_truth_labels[movie2_index, movie1_index] = 1  # Reflective relation

        print("Ground Labels generated")

        for symmetric_group in symmetric_relations:
            # Iterate through each movie in the symmetric group
            for movie_title in symmetric_group:
                # Get the index of the movie in the training data
                searched_movie_index = title_to_index.get(movie_title)

                # Get recommendations for the current movie
                recommendation_data = self.get_recommendations(movie_title)
                recommendations = recommendation_data["recommendations"]
                print(f"got recommendations for {movie_title}")

                # Iterate through recommendations
                for recommendation in recommendations:
                    recommendation_title = recommendation["title"]
                    recommendation_index = title_to_index.get(recommendation_title)

                    # Ensure movie_title is not recommended to itself
                    if searched_movie_index != recommendation_index:
                        # Set both directions in the truth table to 1
                        truth_table_predictions[searched_movie_index, recommendation_index] = 1
                        truth_table_predictions[recommendation_index, searched_movie_index] = 1

        print("Truth Table generated")

        print("Flattening")
        y_ground = ground_truth_labels.flatten()
        y_predict = truth_table_predictions.flatten()

        # Calculate precision, recall, and f1-score
        print("Calculating Scores")
        start_time = time.time()
        precision = precision_score(y_ground, y_predict)
        recall = recall_score(y_ground, y_predict)
        f1 = f1_score(y_ground, y_predict)
        end_time = time.time()

        # Print the metrics
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1-score: {f1:.2f}")
        print(f"Time taken: {end_time - start_time:.4f} seconds")
