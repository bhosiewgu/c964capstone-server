import os
import pickle


class TrainingModule:
    def __init__(self):
        self.training_data_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'training_data.pkl')
        self.similarity_scores_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts',
                                                   'similarity_scores.pkl')
        self.original_movie_data_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts',
                                                     'original_movie_data.pkl')

    def get_training_data_path(self):
        return self.training_data_path

    def get_similarity_scores_path(self):
        return self.similarity_scores_path

    def get_original_movie_data_path(self):
        return self.original_movie_data_path

    def train_model(self):
        if not os.path.exists(self.training_data_path) or not os.path.exists(self.similarity_scores_path) or not os.path.exists(self.original_movie_data_path):
            from modules.MachineLearningModel import MachineLearningModel

            # trains the model when nothing passed in
            print("Training Model Now...")
            model = MachineLearningModel()
            model.pickle_data()
            print("Model Trained!")

    def load_training_data(self):
        with open(self.training_data_path, 'rb') as file:
            return pickle.load(file)

    def load_similarity_scores_data(self):
        with open(self.similarity_scores_path, 'rb') as file:
            return pickle.load(file)

    def load_original_movie_data(self):
        with open(self.original_movie_data_path, 'rb') as file:
            return pickle.load(file)
