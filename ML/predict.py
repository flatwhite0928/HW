import time
import pickle
import csv
import argparse
import pandas as pd
import numpy as np
import os
from keras.models import load_model


def searchfile(path, ext):
    """
    search file with ext in dir, return first file path
    """

    file_list = os.listdir(path)
    for n in file_list:
        if os.path.splitext(n)[1] == ext:
            return os.path.join(path, n)


def predict(rakuten_path, token_path, model_path, encoder_path, output_path, model_select):
    print('reading rakuten data...')
    r_train1, r_label = [], []
    with open(rakuten_path, 'r', newline='') as f:
        readCSV = list(csv.reader(f))
        for i in readCSV:
            r_train1.append(' '.join(eval(i[0])))
            r_label.append(i[1])

    # judge if token model a file
    if os.path.isfile(token_path):
        pass
    elif os.path.isdir(token_path):
        token_path = searchfile(token_path, '.pickle')
        if token_path is None:
            print("Error, cannot find token file in this path")
            exit()
    else:
        print("Error, incorrect token path")
        exit()
    # judge if token model a file
    if os.path.isfile(encoder_path):
        pass
    elif os.path.isdir(encoder_path):
        encoder_path = searchfile(encoder_path, 'pkl')
        if encoder_path is None:
            print("Error, cannot find token file in this path")
            exit()
    else:
        print("Error, incorrect token path")
        exit()
    # judge if model a file
    if os.path.isfile(model_path):
        pass
    elif os.path.isdir(model_path):
        model_path = searchfile(model_path, '.h5')
        if model_path is None:
            print("Error, cannot find model file in this path")
            exit()
    else:
        print("Error, incorrect model path")
        exit()

    with open(token_path, 'rb') as handle:
        token = pickle.load(handle)
    if model_select == 'u':
        r_train_x = token.texts_to_matrix(r_train1)
    elif model_select == 'b':
        r_bigram_train = token.transform(r_train1)
        r_train_x = r_bigram_train.toarray()
    elif model_select == 't':
        r_tfidf_train = token.transform(r_train1)
        r_train_x = r_tfidf_train.todense()
    new_model = load_model(model_path)
    new_model.summary()

    print('predicting...')
    with open(encoder_path, 'rb') as f:
        le = pickle.load(f)
    r_y = new_model.predict(r_train_x)
    predict_ry = le.inverse_transform(np.argmax(r_y, axis=1))

    pre = pd.DataFrame({'id': r_label, 'label': predict_ry})
    filename = output_path + '/label_prediction_' + time.strftime('%m%d-%H-%M') + '.csv'
    with open(filename, 'w', encoding='utf-8') as f:
        pre.to_csv(f)
    print('Saved to ' + filename)


if __name__ == '__main__':
    # ================================================
    # Area: ArgsParse
    # ================================================
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", help="token_path, support path input", required=True)
    parser.add_argument("-r", help="rakuten_path", required=True)
    parser.add_argument("-m", help="model_path, support path input", required=True)
    parser.add_argument("-e", help="encoder_path", required=True)
    parser.add_argument("-o", help="output_path", required=True)
    parser.add_argument("-mo", help="model select b = bigram, u = unigram, t = tfidf", required=True)

    args = parser.parse_args()
    token_path = args.t
    rakuten_path = args.r
    model_path = args.m
    encoder_path = args.e
    output_path = args.o
    model_select = args.mo

    predict(rakuten_path, token_path, model_path, encoder_path, output_path, model_select)
