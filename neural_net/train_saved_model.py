import network
import preprocessing

"""
Script to load a saved model architecture, preprocessing configuration, train the model and validate it
"""

configuration_path = "../model_configurations/" + "zakladni_model/bez-klicovych-slov-2-epoch"
configuration_file = open(configuration_path, "r", encoding='utf-8')
lines = configuration_file.readlines()

model_json = "../model_configurations/model_jsons/" + lines[0][:-1]
preprocessing_configuration = "../model_configurations/tokenizer_configurations/" + lines[1][:-1]
train_dir = "../split_datasets/" + lines[2][:-1]
test_dir = "../split_datasets/" + lines[3][:-1]
epochs = int(lines[4][:-1])
learning_rate = float(lines[5][:-1])
batch_size = int(lines[6])

network.create_model(train_dir, test_dir, preprocessing.Preprocessing().load(preprocessing_configuration),
                                None, "../tensorboard", model_json, epochs, learning_rate, batch_size)


