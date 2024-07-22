import os
import pickle


class TrainingModule:
    def __init__(self):
        self.training_data_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'training_data.pkl')
        self.nearest_neighbors_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts',
                                                   'nearest_neighbors.pkl')
        self.tfid_matrix_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'tfid_matrix.pkl')

    def get_training_data_path(self):
        return self.training_data_path

    def get_nearest_neighbor_path(self):
        return self.nearest_neighbors_path

    def get_tfid_matrix_path(self):
        return self.tfid_matrix_path

    def train_model(self):
        if not os.path.exists(self.training_data_path) or not os.path.exists(self.nearest_neighbors_path) or not os.path.exists(self.tfid_matrix_path):
            from modules.MachineLearningModel import MachineLearningModel

            # trains the model when nothing passed in
            print("Training Model Now...")
            model = MachineLearningModel()
            model.pickle_data()
            print("Model Trained!")

    def load_training_data(self):
        with open(self.training_data_path, 'rb') as file:
            return pickle.load(file)

    def load_nearest_neighbor_data(self):
        with open(self.nearest_neighbors_path, 'rb') as file:
            return pickle.load(file)

    def load_tfid_matrix_data(self):
        with open(self.tfid_matrix_path, 'rb') as file:
            return pickle.load(file)
