from neural_net_code import neural_net
from neural_net_code import preprocessing

"""
Script to load a saved model architecture, preprocessing configuration, train the model and validate it
"""

configuration_path = "../model_config"
configuration_file = open(configuration_path, "r", encoding='utf-8')
lines = configuration_file.readlines()

model_json = lines[0][:-1]
preprocessing_configuration = lines[1][:-1]
train_dir = lines[2][:-1]
test_dir = lines[3]

neural_net.create_model(train_dir, test_dir, preprocessing.Preprocessing().load(preprocessing_configuration),
                        None, "../tensorboard", model_json)


