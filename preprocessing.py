import os
import random
import re
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np
import pickle


class PreprocessingConfig:
    """
    Contains stuff necessary for the model to work
    """
    def __init__(self, emb_matrix, tokenizer, doc_max_len):
        self.emb_matrix = emb_matrix
        self.tokenizer = tokenizer
        self.doc_max_len = doc_max_len


class Preprocessing:
    """
    Performs data preprocessing, defining a vocabulary, Tokenizer instance, and creating an embedding
    matrix
    """
    def __init__(self):
        self.tokenizer = Tokenizer(
            num_words=None,
            filters="!#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n\"\'1234567890",
            lower=True,
            split=' ',
            char_level=False
        )
        self.vocabulary = None
        self.Tokenizer = None
        self.embedding_matrix = None
        self.doc_max_len = 0

    def create_dataset(self, relevant_pages_dir: str, irrelevant_pages_dir: str, train_dir: str, test_dir: str):
        """
        Preprocesses the pages and creates a dataset, then saves vocabulary in a file
        :param relevant_pages_dir: Directory with relevant pages. Inside, a folder for each page is expected. In that folder,
         terms and cookies folders with pages are expected. Folder with no pages in it is ignored
        :param irrelevant_pages_dir: Directory with irrelevant pages. Inside it, files with page contents are expected.
        :param train_dir: Dir to write the training dataset into, contains a file for each page - the format is class text. 0 is irrelevant,
        1 is cookies and 2 is terms
        :param test_dir: Dir to write the testing dataset into, contains a file for each page - the format is class text, one page per line. 0 is irrelevant,
        1 is cookies and 2 is terms
        :param vocab_file: File to which the vocabulary will be saved, words separated by space
        :return: None
        """

        # check if the directories exist
        os.makedirs(relevant_pages_dir, exist_ok=True)
        os.makedirs(irrelevant_pages_dir, exist_ok=True)
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)

        # contains (path, class, train/test)
        pages_info = []

        # collect all page paths
        print("Collecting all page paths")
        tcpaths = self.__collect_rel_pages_paths(relevant_pages_dir)
        terms_pages_paths = tcpaths[0]
        cookies_pages_paths = tcpaths[1]
        irrelevant_pages_paths = self.__collect_irr_pages_paths(irrelevant_pages_dir)

        # split into train and test
        print("Splitting pages into train and test datasets")
        pgs = self.__split_pages(terms_pages_paths)

        # create info
        pinf = self.__create_page_info(pgs[0], 2, True)
        pinf2 = self.__create_page_info(pgs[1], 2, False)
        # add info to pages_info
        [pages_info.append(info) for info in pinf]
        [pages_info.append(info) for info in pinf2]

        # do that for other classes
        pgs = self.__split_pages(cookies_pages_paths)
        pinf = self.__create_page_info(pgs[0], 1, True)
        pinf2 = self.__create_page_info(pgs[1], 1, False)
        [pages_info.append(info) for info in pinf]
        [pages_info.append(info) for info in pinf2]

        pgs = self.__split_pages(irrelevant_pages_paths)
        pinf = self.__create_page_info(pgs[0], 0, True)
        pinf2 = self.__create_page_info(pgs[1], 0, False)
        [pages_info.append(info) for info in pinf]
        [pages_info.append(info) for info in pinf2]

        # shuffle the pages
        random.shuffle(pages_info)

        # create vocab, preprocess pages
        print("Creating vocabulary, writing pages into test and train directories")
        self.vocabulary = dict()
        for i in range(len(pages_info)):
            if pages_info[i][2]:
                target_dir = train_dir
            else:
                target_dir = test_dir
            page_vc = self.__preprocess_page(pages_info[i], target_dir, i)

            for key, value in page_vc.items():
                try:
                    self.vocabulary[key] += value
                except KeyError:
                    self.vocabulary[key] = value

        print("Processing vocabulary")
        self.vocabulary = self.__process_vocabulary(self.vocabulary)

        # create tokenizer and fit it on vocabulary
        text = ""
        for word in self.vocabulary:
            text += word + " "
        self.tokenizer.fit_on_texts([text])
        self.__create_embedding_matrix("fasttext/cc.cs.300.vec")

        return

    def __process_vocabulary(self, vocabulary: dict) -> list:
        """
        Processes vocabulary
        :param vocabulary: vocabulary
        :return: list of words
        """
        min_count = 2
        remove_numbers = True
        remove_stopwords = True

        stopwords = []
        if remove_stopwords:
            sw_file = open("stopwords-cs.txt", "r")
            stopwords = sw_file.readlines()
            for i in range(len(stopwords)):
                stopwords[i] = stopwords[i][0:len(stopwords[i]) - 1]

        new_vocab = []

        for key, value in vocabulary.items():
            add = True
            if value < min_count:
                add = False
            elif remove_numbers and key.isdigit():
                add = False
            if remove_stopwords:
                if key in stopwords:
                    add = False
            if add:
                new_vocab.append(key)

        return new_vocab

    def __create_page_info(self, pages: list, clss: int, is_train: bool) -> list:
        """
        creates info tuples for each page in pages
        :param pages: pages
        :param clss: 0,1,2
        :param is_train:
        :return: tuple (page path, class, is_train)
        """
        infos = []
        for page in pages:
            infos.append((page, clss, is_train))

        return infos

    def __preprocess_page(self, page_info: tuple, target_dir: str, index: int) -> dict:
        """
        Performs preprocessing and saves the result into the target directory. Returns a dictionary with words and counts
        :param page_info: tuple of (source path, class, train/test)
        :param target_dir: target directory
        :param index: index of the page
        :return: dict vocabulary
        """
        with open(page_info[0], "r") as src_file:
            page_lines = src_file.readlines()

        # remove URL and DEPTH
        page_text = ""
        for line in page_lines[2:]:
            page_text += line

        # remove all non-alpha numeric and replace them with space
        page_text = re.sub(r"[\W_]+", ' ', page_text)
        page_tgt_file = open(target_dir + "/" + str(index), "w+")
        page_tgt_file.write(str(page_info[1]) + " " + page_text)
        page_tgt_file.close()

        # create vocabulary
        split_text = page_text.split()
        if len(split_text) > self.doc_max_len:
            self.doc_max_len = len(split_text)
        vc = dict()
        for word in split_text:
            try:
                vc[word.lower()] += 1
            except KeyError:
                vc[word.lower()] = 1

        return vc

    def __collect_rel_pages_paths(self, relevant_dir: str) -> tuple:
        """
        Collects all relevant page paths
        :param relevant_dir: dir
        :return: tuple of (terms paths, cookies paths)
        """
        pages_dirs = os.listdir(relevant_dir)
        cookies_paths = []
        terms_paths = []

        max = 50
        cook = 0
        ter = 0
        for pdir in pages_dirs:
            cookies_files = os.listdir(relevant_dir + "/" + pdir + "/cookies")
            terms_files = os.listdir(relevant_dir + "/" + pdir + "/terms")

            if len(cookies_files) != 0 and cook < max:
                [cookies_paths.append(relevant_dir + "/" + pdir + "/cookies/" + file) for file in cookies_files]

            if len(terms_files) != 0 and ter < max:
                [terms_paths.append(relevant_dir + "/" + pdir + "/terms/" + file) for file in terms_files]

            cook += len(cookies_files)
            ter += len(terms_files)

        return terms_paths, cookies_paths

    def __collect_irr_pages_paths(self, irrelevant_dir: str) -> list:
        """
        Collects irrelevant page paths
        :param irrelevant_dir: dir
        :return: list of irrelevant page paths
        """
        max = 50
        files = os.listdir(irrelevant_dir)
        paths = []

        for i in range(max):
            paths.append(irrelevant_dir + "/" + files[i])

        [paths.append(irrelevant_dir + "/" + file) for file in files]

        return paths

    def __split_pages(self, pages: list) -> tuple:
        """
        Splits pages list into training pages and testing pages
        :param pages: list of pages
        :return: tuple of training pages, testing pages
        """
        test_size = 0.25
        test_count = int(len(pages) * test_size)
        test_pages = []

        # get test pages
        for i in range(test_count):
            r = random.randrange(len(pages))
            test_pages.append(pages[r])
            pages.remove(pages[r])

        # train pages are the leftover pages
        train_pages = pages

        return train_pages, test_pages

    def __create_embedding_matrix(self, fasttext_path: str):
        """
        Saves embedding vectors based on Tokenizer indexing
        :param fasttext_path: Path to fasttext pretrained embeddings
        :return: None
        """
        ft_file = open(fasttext_path, "r+")
        word_index = self.tokenizer.word_index
        self.embedding_matrix = np.zeros((len(word_index) + 1, 300))

        print("Parsing fasttext embeddings")
        ft_file.readline()  # read dimensions
        while True:
            line = ft_file.readline()
            if line == "":
                break
            word = line.split()[0]
            try:
                if word_index[word] is not None:
                    vector = []
                    for e in line.split()[1:]:
                        vector.append(float(e))
                    self.embedding_matrix[word_index[word]] = vector
            except KeyError:
                continue

        ft_file.close()

    @staticmethod
    def load(config_path) -> PreprocessingConfig:
        """
        Loads the relevant objects into PreprocessingConfig
        :param config_path: File to load the config from
        :return:
        """
        return pickle.load(open(config_path, "rb"))

    def save(self, config_path):
        """
        Dumps the relevant objects into a pickle
        :param config_path: File to save the config to
        :return:
        """
        config = PreprocessingConfig(self.embedding_matrix, self.tokenizer, self.doc_max_len)
        pickle.dump(config, open(config_path, "wb"))

