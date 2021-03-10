from neural_net_code import neural_net, preprocessing

"""
File to create the dataset, tokenizer, embedding matrix and train the network
"""

# create instance
preprocessing = preprocessing.Preprocessing()

# if we want to create dataset and tokenizer
preprocessing.create_dataset("raw_datasets/pages-merged", "raw_datasets/irrelevant-new", "./../train-created", "./../test-created", "D:\\fasttext\\cc.cs.300.vec")

# if we want to save it
preprocessing.save("./../saved_preprocessing_configuration")

# load the config
config = preprocessing.load("./../saved_preprocessing_configuration")

# train the network
neural_net.create_model("./../train-created", "./../test-created", config, "./../saved-model", "./../tensorboard")