import preprocessing

"""
A script to create a new test/train split and a new tokenizer 
"""

# relevant pages from crawler, expects the same structure the crawler has generated
pages_dir = "../raw_datasets/pages"

# irrelevant pages from crawler, expects a directory with page files in it
irrelevant_dir = "../raw_datasets/irrelevant"

# directory the test dataset will be in
test_dir = "test_created"

# directory the train dataset will be in
train_dir = "train_created"

# path to text fasttext file for czech language
# download from https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cs.300.vec.gz
# in the same directory as the text fasttext file has to be a binary fasttext file for creating oov vectors
# download from https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cs.300.bin.gz
fasttext_file = "D:/fasttext/cc.cs.300.vec" #/path/to/fasttext/vectors/cc.cs.300.vec"

# created tokenizer file
tokenizer_file = "preprocessing-config-with-keyw"

# filter out keywords
filter_keywords = False


# create instance of preprocessor
prep_conf = preprocessing.Preprocessing()

# preprocess the data, create test/train split, fit the tokenizer on the vocabulary
prep_conf.create_dataset(pages_dir, irrelevant_dir, train_dir, test_dir, fasttext_file, filter_keywords)

# save the created tokenizer, embedding matrix and maximum length of a document
prep_conf.save(tokenizer_file)
