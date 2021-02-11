import os
import random
import re


def create_dataset(relevant_pages_dir: str, irrelevant_pages_dir: str, train_dir: str, test_dir: str, vocab_file: str):
    """
    Preprocesses the pages and creates a dataset, then saves vocabulary in a file
    :param relevant_pages_dir: Directory with relevant pages. Inside, a folder for each page is expected. In that folder,
     terms and cookies folders with pages are expected. Folder with no pages in it is ignored
    :param irrelevant_pages_dir: Directory with irrelevant pages. Inside it, files with page contents are expected.
    :param train_dir: Dir to write the training dataset into, contains a file for each page - the format is class;text. 0 is irrelevant,
    1 is cookies and 2 is terms
    :param test_dir: Dir to write the testing dataset into, contains a file for each page - the format is class;text, one page per line. 0 is irrelevant,
    1 is cookies and 2 is terms
    :param vocab_file: File to which the vocabulary will be saved, words separated by space
    :return: None
    """

    # check if the directories exist
    os.makedirs(relevant_pages_dir, exist_ok=True)
    #os.makedirs(irrelevant_pages_dir, exist_ok=True)
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # contains (path, class, train/test)
    pages_info = []

    # collect all page paths
    print("Collecting all page paths")
    tcpaths = collect_rel_pages_paths(relevant_pages_dir)
    terms_pages_paths = tcpaths[0]
    cookies_pages_paths = tcpaths[1]
    #irrelevant_pages_paths = collect_irr_pages_paths(irrelevant_pages_dir)

    # split into train and test
    print("Splitting pages into train and test datasets")
    pgs = split_pages(terms_pages_paths)

    # create info
    pinf = create_page_info(pgs[0], 2, True)
    pinf2 = create_page_info(pgs[1], 2, False)

    # add info to pages_info
    [pages_info.append(info) for info in pinf]
    [pages_info.append(info) for info in pinf2]

    # do that for other classes
    pgs = split_pages(cookies_pages_paths)
    pinf = create_page_info(pgs[0], 1, True)
    pinf2 = create_page_info(pgs[1], 1, False)
    [pages_info.append(info) for info in pinf]
    [pages_info.append(info) for info in pinf2]

    #pgs = split_pages(irrelevant_pages_paths)
    #pinf = create_page_info(pgs[0], 0, True)
    #pinf2 = create_page_info(pgs[1], 0, False)
    #[pages_info.append(info) for info in pinf]
    #[pages_info.append(info) for info in pinf2]

    # shuffle the pages
    random.shuffle(pages_info)

    # create vocab, preprocess pages
    print("Creating vocabulary, writing pages into test and train directories")
    vocabulary = dict()
    for i in range(len(pages_info)):
        if pages_info[i][2]:
            target_dir = train_dir
        else:
            target_dir = test_dir
        page_vc = preprocess_page(pages_info[i], target_dir, i)

        for key, value in page_vc.items():
            try:
                vocabulary[key] += value
            except KeyError:
                vocabulary[key] = value

    print("Processing vocabulary")
    vocabulary = process_vocabulary(vocabulary)
    vc_file = open(vocab_file, "w+")
    for word in vocabulary:
        vc_file.write(word + " ")

    vc_file.close()
    return


def process_vocabulary(vocabulary: dict) -> list:
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
        if remove_numbers and key.isdigit():
            add = False
        if remove_stopwords:
            if key in stopwords:
                add = False

        if add:
            new_vocab.append(key)

    return new_vocab


def create_page_info(pages: list, clss: int, is_train: bool) -> list:
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


def preprocess_page(page_info: tuple, target_dir: str, index: int) -> dict:
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
    page_tgt_file.write(str(page_info[1]) + ";" + page_text)
    page_tgt_file.close()

    # create vocabulary
    split_text = page_text.split()
    vc = dict()
    for word in split_text:
        try:
            vc[word.lower()] += 1
        except KeyError:
            vc[word.lower()] = 1

    return vc


def collect_rel_pages_paths(relevant_dir: str) -> tuple:
    """
    Collects all relevant page paths
    :param relevant_dir: dir
    :return: tuple of (terms paths, cookies paths)
    """
    pages_dirs = os.listdir(relevant_dir)
    cookies_paths = []
    terms_paths = []

    for pdir in pages_dirs:
        cookies_files = os.listdir(relevant_dir + "/" + pdir + "/cookies")
        terms_files = os.listdir(relevant_dir + "/" + pdir + "/terms")

        if len(cookies_files) != 0:
            [cookies_paths.append(relevant_dir + "/" + pdir + "/cookies/" + file) for file in cookies_files]

        if len(terms_files) != 0:
            [terms_paths.append(relevant_dir + "/" + pdir + "/terms/" + file) for file in terms_files]

    return terms_paths, cookies_paths


def collect_irr_pages_paths(irrelevant_dir: str) -> list:
    """
    Collects irrelevant page paths
    :param irrelevant_dir: dir
    :return: list of irrelevant page paths
    """
    files = os.listdir(irrelevant_dir)
    paths = []
    [paths.append(irrelevant_dir + "/" + file) for file in files]

    return paths


def split_pages(pages: list) -> tuple:
    """
    Splits pages list into training pages and testing pages
    :param pages: list of pages
    :return: tuple of training pages, testing pages
    """
    test_size = 0.1
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
