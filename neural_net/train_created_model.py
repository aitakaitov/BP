from sys import argv

import network
from preprocessing import Preprocessing

# train dataset directory
train_dir = "train_created"

# test dataset directory
test_dir = "test_created"

# preprocessing configuration
prep_config_file = "preprocessing-config-no-keyw"

configuration_path = "../model_configurations/" + argv[1]
configuration_file = open(configuration_path, "r", encoding='utf-8')
lines = configuration_file.readlines()

model_json = "../model_configurations/model_jsons/" + lines[0][:-1]
preprocessing_configuration = Preprocessing().load(prep_config_file)
epochs = int(lines[4][:-1])
learning_rate = float(lines[5][:-1])
batch_size = int(lines[6])


network.create_model(train_dir, test_dir, preprocessing_configuration,
                                None, "../tensorboard", model_json, epochs, learning_rate, batch_size)




