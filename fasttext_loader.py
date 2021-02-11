
def create_embedding_matrix(vocab_path: str, fasttext_path: str, emb_path: str):
    """
    Saves embedding vectors based on supplied pretrained embeddings and vocabulary
    :param vocab_path: Path to file with vocabulary, words separated by spaces
    :param fasttext_path: Path to fasttext pretrained embeddings
    :param emb_path: Path to output file - one word per line in format "word v1 v2 ... v300"
    :return: None
    """
    ft_file = open(fasttext_path, "r+")
    word_pos_dict = dict()

    print("Parsing fasttext embeddings")
    ft_file.readline()  # read dimensions
    while True:  # make linepos table for each word
        line = ft_file.readline()
        if line == "":
            break
        pos = ft_file.tell() - len(line)
        word = line.split()[0]
        word_pos_dict[word] = pos

    print("Loading vocabulary")
    vc_file = open(vocab_path, "r")         # load the vocabulary
    vocab = vc_file.read().split()
    vc_file.close()

    print("Writing embeddings into file")
    emb_file = open(emb_path, "w+")         # save embeddings into file
    for word in vocab:
        try:
            pos = word_pos_dict[word]
        except KeyError:
            continue

        ft_file.seek(pos)
        emb_file.write(ft_file.readline())

    ft_file.close()
    emb_file.close()
