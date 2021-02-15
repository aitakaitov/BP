from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
import numpy as np
from preprocessing import Preprocessing
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras

def create_model(train_dir, test_dir, model_path, tokenizer_path, preprocessor: Preprocessing):
    embedding_dim = preprocessor.embedding_matrix.shape[1]     # how large will the embedded vectors be
    input_length = preprocessor.doc_max_len      # how many words will be supplied in a document
    input_dim = len(preprocessor.tokenizer.word_index) + 1       # how long is OHE of a word
    embedding_weights = preprocessor.embedding_matrix  # embedding matrix of size input_dim x embedding_dim

    input = layers.Input(shape=(None,), dtype='int64')

    embedding_0 = layers.Embedding(
        input_dim=input_dim,
        output_dim=embedding_dim,
        input_length=input_length,
        weights=[embedding_weights],
        trainable=False
    )(input)

    reshape_0 = layers.Reshape((
        input_length,
        embedding_dim
    ))(embedding_0)

    conv_0 = layers.Conv1D(
        filters=32,
        kernel_size=8,
        activation='relu'
    )(reshape_0)

    conv_1 = layers.Conv1D(
        filters=32,
        kernel_size=6,
        activation='relu'
    )(reshape_0)

    conv_2 = layers.Conv1D(
        filters=32,
        kernel_size=4,
        activation='relu'
    )(reshape_0)

    maxpool_0 = layers.MaxPooling1D(
        pool_size=4
    )(conv_0)

    maxpool_1 = layers.MaxPooling1D(
        pool_size=4
    )(conv_1)

    maxpool_2 = layers.MaxPooling1D(
        pool_size=4
    )(conv_2)

    concat = layers.Concatenate(axis=1)([maxpool_0, maxpool_1, maxpool_2])
    flatten = layers.Flatten()(concat)
    dense_0 = layers.Dense(units=32, activation='relu')(flatten)
    output = layers.Dense(units=1, activation='relu')(dense_0)

    model = tensorflow.keras.models.Model(input, output)

    # define the model
    #model = Sequential()
    #model.add(layers.Embedding(
    #    input_dim=input_dim,
    #    output_dim=embedding_dim,
    #    input_length=input_length,
    #    weights=[embedding_weights],
    #    trainable=False
    #))
    #model.add(layers.Conv1D(filters=64, kernel_size=8, activation='relu'))
    #model.add(layers.MaxPooling1D(pool_size=2))
    #model.add(layers.Conv1D(filters=48, kernel_size=8, activation='relu'))
    #model.add(layers.MaxPooling1D(pool_size=2))
    #model.add(layers.Conv1D(filters=32, kernel_size=8, activation='relu'))
    #model.add(layers.MaxPooling1D(pool_size=2))
    #model.add(layers.Flatten())
    #model.add(layers.Dense(128, activation='relu'))
    #model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()

    # prepare training and testing data
    X_train, y_train = get_dataset(train_dir, preprocessor.tokenizer, preprocessor.doc_max_len)
    X_test, y_test = get_dataset(test_dir, preprocessor.tokenizer, preprocessor.doc_max_len)

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=8, batch_size=8)

    return


def get_dataset(dir: str, tokenizer, max_len):
    files = os.listdir(dir)
    X = np.zeros((len(files), max_len))
    y = np.zeros((len(files), 1))
    i = 0
    for file in files:
        with open(dir + "/" + file) as f:
            text = f.read()
            if text[0] == '1':
                y[i][0] = 0
            if text[0] == '2':
                y[i][0] = 1

            X[i] = pad_sequences([tokenizer.texts_to_sequences([text[2:]])[0]], maxlen=max_len)
            i += 1

    return np.array(X), np.array(y)


def train_model():

    return


def test_model():

    return
