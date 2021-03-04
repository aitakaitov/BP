from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
import numpy as np
from preprocessing import PreprocessingConfig
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow


def create_model(train_dir: str, test_dir: str, preprocessor: PreprocessingConfig, model_path=None, tb_logdir=None):
    """
    Creates, trains and validates a model
    :param train_dir: directory with files containing training pages
    :param test_dir: directory with files containing testing pages
    :param preprocessor: PreprocessorConfig - contains embedding matrix, Tokenizer and maximum document length
    :param model_path: Path to save the trained model. If None, model is not saved
    :param tb_logdir: Path to save the Tensorboard logs. If None, logs are not saved and displayed
    :return: None
    """
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    embedding_dim = preprocessor.emb_matrix.shape[1]     # how large will the embedded vectors be
    input_length = preprocessor.doc_max_len      # how many words will be supplied in a document
    input_dim = len(preprocessor.tokenizer.word_index) + 1       # how long is OHE of a word
    embedding_weights = preprocessor.emb_matrix  # embedding matrix of size input_dim x embedding_dim

    # switch between sequential and parallel models
    sequential = True

    if not sequential:
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
            kernel_size=6
        )(reshape_0)

        conv_1 = layers.Conv1D(
            filters=32,
            kernel_size=4
        )(reshape_0)

        conv_2 = layers.Conv1D(
            filters=32,
            kernel_size=2
        )(reshape_0)

        norm_0 = layers.BatchNormalization()(conv_0)
        norm_1 = layers.BatchNormalization()(conv_1)
        norm_2 = layers.BatchNormalization()(conv_2)

        act_0 = layers.Activation(tensorflow.keras.activations.relu)(norm_0)
        act_1 = layers.Activation(tensorflow.keras.activations.relu)(norm_1)
        act_2 = layers.Activation(tensorflow.keras.activations.relu)(norm_2)

        glomax_pool_0 = layers.GlobalMaxPool1D()(act_0)
        glomax_pool_1 = layers.GlobalMaxPool1D()(act_1)
        glomax_pool_2 = layers.GlobalMaxPool1D()(act_2)

        concat_0 = layers.Concatenate(axis=1)([glomax_pool_0, glomax_pool_1, glomax_pool_2])
        dropout_0 = layers.Dropout(0.3)(concat_0)
        flatten = layers.Flatten()(dropout_0)
        dense_0 = layers.Dense(units=24, activation='relu')(flatten)
        output = layers.Dense(units=3, activation='softmax')(dense_0)
        model = tensorflow.keras.models.Model(input, output)
    else:

        model = Sequential()
        model.add(layers.Embedding(
            input_dim=input_dim,
            output_dim=embedding_dim,
            input_length=input_length,
            weights=[embedding_weights],
            trainable=False
        ))
        model.add(layers.Conv1D(filters=32, kernel_size=3))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation(tensorflow.keras.activations.relu))
        model.add(layers.MaxPooling1D(pool_size=2))
        model.add(layers.Conv1D(filters=32, kernel_size=4))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation(tensorflow.keras.activations.relu))
        model.add(layers.MaxPooling1D(pool_size=5))
        model.add(layers.Conv1D(filters=32, kernel_size=8))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation(tensorflow.keras.activations.relu))
        model.add(layers.MaxPooling1D(pool_size=12))
        model.add(layers.Flatten())
        model.add(layers.Dropout(0.25))
        model.add(layers.Dense(32, activation='relu'))
        model.add(layers.Dense(3, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()

    # prepare training and testing data
    X_train, y_train = get_dataset(train_dir, preprocessor.tokenizer, preprocessor.doc_max_len)
    X_test, y_test = get_dataset(test_dir, preprocessor.tokenizer, preprocessor.doc_max_len)

    # train with logging callback
    if tb_logdir is not None:
        tensorboard_callback = tensorflow.keras.callbacks.TensorBoard(log_dir=tb_logdir, histogram_freq=1)
        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=8, batch_size=32, callbacks=[tensorboard_callback])
    else:
        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=6, batch_size=2)

    # save the model
    if model_path is not None:
        model.save(model_path, overwrite=False, include_optimizer=True)

    return


def get_dataset(dir: str, tokenizer, max_len) -> tuple:
    """
    Loads pages from a directory and returns their vectors and labels
    :param dir: directory
    :param tokenizer: Tokenizer
    :param max_len: maximum document length
    :return: Tuple of (X, y)
    """
    files = os.listdir(dir)
    X = np.zeros((len(files), max_len))
    y = np.zeros((len(files), 3))
    i = 0
    for file in files:
        with open(dir + "/" + file, "r", encoding='utf-8') as f:
            text = f.read()
            y[i][int(text[0])] = 1
            X[i] = pad_sequences([tokenizer.texts_to_sequences([text[2:]])[0]], maxlen=max_len, truncating="post")
            i += 1

    return np.array(X), np.array(y)


