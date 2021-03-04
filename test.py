import preprocessing
import neural_net

"""
File to create the dataset, tokenizer, embedding matrix and train the network
"""

# create instance
preprocessing = preprocessing.Preprocessing()

# if we want to create dataset and tokenizer
#preprocessing.create_dataset("pages-merged", "irrelevant-new", "train-shuffled-4", "test-shuffled-4", "D:\\fasttext\\cc.cs.300.vec")

# if we want to save it
#preprocessing.save("prep-config-merge-false-docmax10000-keyw")

# load the config
config = preprocessing.load("prep-config-merge-false-docmax10000-keyw")

# train the network
neural_net.create_model("train-shuffled-4", "test-shuffled-4", config, "saved-model", "tensorboard")