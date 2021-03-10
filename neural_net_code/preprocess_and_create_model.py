from neural_net_code import neural_net, preprocessing
import os.path

"""
A script to create a new test/train split, a new tokenizer and to train the neural network
Saves the tokenizer, embedding matrix, model architecture (without weights), trained model and tensorboard logs
"""

# create instance of preprocessor
preprocessing = preprocessing.Preprocessing()

# preprocess the data, create test/train split, fit the tokenizer on the vocabulary
#preprocessing.create_dataset("../raw_datasets/pages-merged", "../raw_datasets/irrelevant-new", "../train-created", "../test-created", "D:\\fasttext\\cc.cs.300.vec")

# save the created tokenizer, embedding matrix and maximum length of a document
#preprocessing.save("../saved_preprocessing_configuration")

# load the tokenizer, embedding matrix and maximum document length
config = preprocessing.load("../saved_preprocessing_configuration")

# train the network, save the architecture and trained model, log tensorboard and validate the network on annotated data
neural_net.create_model("../split_datasets/train-shuffled-4", "../split_datasets/test-shuffled-4", config, "../saved-model", "../tensorboard")