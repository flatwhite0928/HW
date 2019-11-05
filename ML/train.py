import pickle
import numpy as np
import pandas as pd
import argparse

from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Input, Dropout, Activation
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


# for unigram model
def train_unigram(shopstyle_path, output_path, max_words, seed, batch_size, epoch):

    print('reading data...')
    df = pd.read_csv(shopstyle_path, header=None)
    corpus = df.replace(to_replace='None', value=np.nan).dropna()
    train1 = [' '.join(eval(i)) for i in corpus[0]]

    target = corpus[1].apply(lambda x: x.replace('_', ' ')).values
    le = LabelEncoder()
    le.fit(target)
    y = le.transform(target)
    nclass = len(list(le.classes_))
    with open(output_path + '/encoder.pkl', 'wb') as f:
        pickle.dump(le, f)

    x_train, x_test, y_train, y_test = train_test_split(train1, y, test_size=0.2,
                                                        random_state=seed)

    print('building tokenizer...')
    tokenize = Tokenizer(num_words=max_words, char_level=False)
    tokenize.fit_on_texts(x_train)
    with open(output_path + '/tokenizer_unigram_' + str(max_words) + '.pickle',
              'wb') as handle:
        pickle.dump(tokenize, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('building features...')
    x_train1 = tokenize.texts_to_matrix(x_train)
    x_test1 = tokenize.texts_to_matrix(x_test)
    labels_train = to_categorical(np.asarray(y_train))
    labels_test = to_categorical(np.asarray(y_test))

    print('training model...')
    model = Sequential()
    model.add(Dense(512, input_shape=(max_words,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nclass))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.fit(x_train1, labels_train,
              batch_size=batch_size,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    model.fit(x_train1, labels_train,
              batch_size=batch_size//2,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    score = model.evaluate(x_test1, labels_test, batch_size=batch_size, verbose=1)
    print('Test accuracy:', score[1])
    filename = output_path + '/categorization_unigram_' + str(max_words) + '.h5'
    model.save(filename)
    print('Saved to ' + filename)


# for bigram model
def train_bigram(shopstyle_path, output_path, min_df, seed, batch_size, epoch):

    print('reading data...')
    df = pd.read_csv(shopstyle_path, header=None)
    corpus = df.replace(to_replace='None', value=np.nan).dropna()
    train1 = [' '.join(eval(i)) for i in corpus[0]]

    target = corpus[1].apply(lambda x: x.replace('_', ' ')).values
    le = LabelEncoder()
    le.fit(target)
    y = le.transform(target)
    nclass = len(list(le.classes_))

    x_train, x_test, y_train, y_test = train_test_split(train1, y, test_size=0.2,
                                                        random_state=seed)

    print('building vectorizer...')
    vectorizer = CountVectorizer(min_df=min_df, ngram_range=(1, 2))
    bigram_train = vectorizer.fit_transform(x_train)
    bigram_test = vectorizer.transform(x_test)
    names = vectorizer.get_feature_names()
    print('vectorizer size: ' + str(len(names)))
    with open(output_path + '/vectorizer_bigram_' + str(min_df) + '.pickle',
              'wb') as handle:
        pickle.dump(vectorizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('building features...')
    bi_train = bigram_train.toarray()
    bi_test = bigram_test.toarray()
    labels_train = to_categorical(np.asarray(y_train))
    labels_test = to_categorical(np.asarray(y_test))

    print('training model...')
    model = Sequential()
    model.add(Dense(512, input_shape=(len(names),)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nclass))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.fit(bi_train, labels_train,
              batch_size=batch_size,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    model.fit(bi_train, labels_train,
              batch_size=batch_size//2,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    score = model.evaluate(bi_test, labels_test, batch_size=batch_size, verbose=1)
    print('Test accuracy:', score[1])
    filename = output_path + '/categorization_bigram_' + str(min_df) + '.h5'
    model.save(filename)
    print('Saved to ' + filename)

    
# for tf-idf    
def train_tfidf(shopstyle_path, output_path, max_words, seed, batch_size, epoch):

    print('reading data...')
    df = pd.read_csv(shopstyle_path, header=None)
    corpus = df.replace(to_replace='None', value=np.nan).dropna()
    train1 = [' '.join(eval(i)) for i in corpus[0]]

    target = corpus[1].apply(lambda x: x.replace('_', ' ')).values
    le = LabelEncoder()
    le.fit(target)
    y = le.transform(target)
    nclass = len(list(le.classes_))

    x_train, x_test, y_train, y_test = train_test_split(train1, y, test_size=0.2,
                                                        random_state=seed)

    print('building vectorizer...')
    tfidf_vectorizer = TfidfVectorizer(max_features=max_words, use_idf=True)
    tfidf_train = tfidf_vectorizer.fit_transform(x_train)
    tfidf_test =  tfidf_vectorizer.transform(x_test)
    names = tfidf_vectorizer.get_feature_names()
    print('vectorizer size: ' + str(len(names)))
    with open(output_path + '/vectorizer_tfidf_' + str(max_words) + '.pickle',
              'wb') as handle:
        pickle.dump(tfidf_vectorizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print('building features...')
    tf_train = tfidf_train.todense()
    tf_test = tfidf_test.todense()
    labels_train = to_categorical(np.asarray(y_train))
    labels_test = to_categorical(np.asarray(y_test))

    print('training model...')
    model = Sequential()
    model.add(Dense(512, input_shape=(len(names),)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nclass))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.fit(tf_train, labels_train,
              batch_size=batch_size,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    model.fit(tf_train, labels_train,
              batch_size=batch_size//2,
              epochs=epoch,
              verbose=1,
              validation_split=0.1)

    score = model.evaluate(tf_test, labels_test, batch_size=batch_size, verbose=1)
    print('Test accuracy:', score[1])
    filename = output_path + '/categorization_tfidf_' + str(max_words) + '.h5'
    model.save(filename)
    print('Saved to ' + filename)
    

if __name__ == '__main__':
    # ================================================
    # Area: ArgsParse
    # ================================================
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="shopstyle_path", required=True)
    # parser.add_argument("-r", help="rakuten_path", required=True)
    parser.add_argument("-o", help="output_path", required=True)
    parser.add_argument("-m", help="min_df or max_words", type=int, required=True)
    parser.add_argument("-se", help="seed", type=int, default=42)
    parser.add_argument("-b", help="batch_size", type=int, required=True)
    parser.add_argument("-e", help="epoch", type=int, required=True)
    parser.add_argument("-mo", help="model select b = bigram, u = unigram, t = tfidf", default="b", required=True)

    args = parser.parse_args()
    shopstyle_path = args.s
    # rakuten_path = args.r
    output_path = args.o
    min_df = args.m
    seed = args.se
    batch_size = args.b
    epoch = args.e
    mode_select = args.mo
    # ================================================
    # Area: 
    # ================================================
    if mode_select == "b":
        train_bigram(shopstyle_path, output_path, min_df, seed, batch_size, epoch)
    elif mode_select == "u":
        train_unigram(shopstyle_path, output_path, min_df, seed, batch_size, epoch)
    elif mode_select == "t":
        train_tfidf(shopstyle_path, output_path, min_df, seed, batch_size, epoch)
