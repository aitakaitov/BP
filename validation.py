import preprocessing
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os
import numpy as np

config = preprocessing.Preprocessing().load("C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\prep-config-merge-false-docmax10000-keyw")
tokenizer = config.tokenizer
max_len = config.doc_max_len
model = load_model('C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\saved-model')
model.summary()

files = os.listdir('C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\manual-validation-complete')
files.sort()
urls = []
X = np.zeros((len(files), max_len))
i = 0
for file in files:
    with open("C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\manual-validation-complete\\" + file, "r", encoding='utf-8') as f:
        lines = f.readlines()
        text = ""
        urls.append(lines[0][5:])
        for line in lines[2:]:
            text += line

        X[i] = pad_sequences([tokenizer.texts_to_sequences([text])[0]], maxlen=max_len)
        i += 1

res_file = open("C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\results-manual", "w+", encoding='utf-8')
predictions = model.predict(X, batch_size=None, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False)

for i in range(len(files)):
    maximum = max(predictions[i][0], predictions[i][1], predictions[i][2])

    if predictions[i][0] == maximum:
        line = "IRRELEVANT" + "\t" + urls[i]
        res_file.writelines([line])
    elif predictions[i][1] == maximum:
        line = "COOKIES" + "\t" + urls[i]
        res_file.writelines([line])
    elif predictions[i][2] == maximum:
        line = "TERMS" + "\t" + urls[i]
        res_file.writelines([line])


res_file.close()

input_file = open("C:\\Users\\Vojtěch Bartička\\Desktop\\BP\\BP\\results-manual", "r", encoding='utf-8')
reference_file = open("/validation-reference", "r", encoding='utf-8')

input_lines = input_file.readlines()
reference_lines = reference_file.readlines()

ref_index = dict()
ref_index["TERMS"] = 0
ref_index["COOKIES"] = 1
ref_index["IRRELEVANT"] = 2
conf_matrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, "X"]]
for i in range(len(reference_lines)):
    input_line = input_lines[i].split()
    reference_line = reference_lines[i].split()
    conf_matrix[ref_index[input_line[0]]][ref_index[reference_line[0]]] += 1

for i in range(3):
    try:
        conf_matrix[i][int(3)] = conf_matrix[i][i] / (conf_matrix[i][0] + conf_matrix[i][1] + conf_matrix[i][2])
    except ZeroDivisionError:
        conf_matrix[i][3] = "NaN"

for i in range(3):
    try:
        conf_matrix[3][i] = conf_matrix[i][i] / (conf_matrix[0][i] + conf_matrix[1][i] + conf_matrix[2][i])
    except ZeroDivisionError:
        conf_matrix[3][i] = "NaN"

col_width = 20
for row in conf_matrix:
    print("".join(str(word).ljust(col_width) for word in row))

precisions = []
recalls = []

for i in range(3):
    try:
        row_prec = conf_matrix[i][i] / (conf_matrix[i][0] + conf_matrix[i][1] + conf_matrix[i][2])
    except ZeroDivisionError:
        row_prec = "NaN"
    precisions.append(row_prec)

for i in range(3):
    try:
        col_rec = conf_matrix[i][i] / (conf_matrix[0][i] + conf_matrix[1][i] + conf_matrix[2][i])
    except ZeroDivisionError:
        col_rec = "NaN"
    recalls.append(col_rec)

print("Presnost: {}".format((precisions[0] + precisions[1] + precisions[2]) / 3))
print("Uplnost: {}".format((recalls[0] + recalls[1] + recalls[2]) / 3))



