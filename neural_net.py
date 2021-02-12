from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
import numpy as np

def create_model(emb_matrix_path, train_dir, test_dir, model_path):
    embedding_dim = 300     # how large will the embedded vectors be
    input_length = 200      # how many words will be supplied in a document
    input_dim = 20000       # how long is OHE of a word
    embedding_weights = []  # embedding matrix of size input_dim x embedding_dim

    model = Sequential()
    model.add(layers.Embedding(
        input_dim=input_dim,
        output_dim=embedding_dim,
        input_length=input_length,
        embeddings_initializer=embedding_weights,
        trainable=False
    ))
    return


def parse_embedding_matrix(emb_matrix_path) -> tuple:
    with open(emb_matrix_path, "w") as f:
        file_lines = f.readlines()

    vocab = []
    embedding_matrix = []

    for line in file_lines:
        split_line = line.split()
        vocab.append(split_line[0])
        vector = []
        for e in split_line[1:]:
            vector.append(float(e))

        embedding_matrix.append(vector)

    return vocab, embedding_matrix

def train_model():

    return


def test_model():

    return
