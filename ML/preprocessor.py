# -*- coding: utf-8 -*-
"""
Pre-processing
"""
import re
import csv
import time
import nltk
import string
import argparse
import gc

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def clean_train(text):
    """
    Lower-case, tokenize, stem,
    Removal: digits + punctuations + white spaces + stopwords
    """
    text = re.sub(r'\d+', '', text).lower()
    text = text.replace(" • ", "")
    text = text.replace("-", " ")
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip()
    text = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    text = [i for i in text if i not in stop_words]
    stemmer = SnowballStemmer(language='english')
    text = [stemmer.stem(t) for t in text]
    return text


def csv_mapping(mapping_csv_path):
    mapping_table = {}
    with open(mapping_csv_path, 'r', newline='', encoding='utf-8', errors="ignore") as csv2:
        rows = csv.reader(csv2)
        for n in rows:
            if n[1] not in mapping_table:
                mapping_table[n[1]] = n[0]
    return mapping_table

    
def pre_processing():
    global csv_input_path
    global csv_output_path
    global chop_threshold
    global random_mode
    global loop_filling
    global mapping_csv_path
    # Load Data
    print("Preprocessing...")
    with open(csv_input_path, 'r', newline='', encoding='utf-8', errors="ignore") as csv2:
        raw = csv.reader(csv2)
        print("Raw data loaded, Start Merge Name and Description")

        # Merge Name and Description
        pre_train = []
        for p in raw:
            pre_train.append([p[0] + " " + p[1], p[2]])
        del raw
        gc.collect()
        print("Merge Name and Description Completed, start Mapping") 

        # mapping
        if ship_mapping is True:
            train_data_mapping = pre_train
        else:
            miss_category = {}
            train_data_mapping = []
            lookup = csv_mapping(mapping_csv_path)
            for p in pre_train:
                #

                # if analysis miss category
                if writing_list[1] is None and category_miss_path is not None:
                    if shopstyle_category in miss_category:
                        miss_category[shopstyle_category] += 1
                    else:
                        miss_category[shopstyle_category] = 1
            # writing to miss.csv
            if category_miss_path is not None:
                try:
                    print("Written miss category to", category_miss_path)
                    with open(category_miss_path, 'a', newline='', encoding='utf-8', errors='ignore') as csv1:
                        csv_write = csv.writer(csv1, dialect='excel')
                        for k, v in miss_category.items():
                            csv_write.writerow([k, v])
                except Exception as e:
                    print("Writing Error, please spicfy correct path to store missed category\n", e)
        del pre_train
        gc.collect()
        print("Mapping completed, Start balancing data.")

        # Chop balanced data
        cate_num = {}
        train_data = []
        # unlimited
        if chop_threshold == 0:
            for p in train_data_mapping:
                # fliter miss category
                if p[1] is None:
                    continue
                else:
                    train_data.append(p)
        # limited and Sequential balancing
        elif chop_threshold != 0 and random_mode is False:
            for p in train_data_mapping:
                # balanced data
                if p[1] is not None and p[1] not in cate_num:
                    cate_num[p[1]] = 1
                    train_data.append(p)
                else:
                    # if mapping non-miss, add to train_data
                    if p[1] is not None and cate_num[p[1]] < chop_threshold:
                        train_data.append(p)
                        cate_num[p[1]] += 1
        # limited and random balancing
        elif chop_threshold != 0 and random_mode is True:
            import random
            # add all non-miss data in to a dict
            train_data_dict = {}
            for p in train_data_mapping:
                if p[1] is not None and p[1] not in train_data_dict:
                    train_data_dict[p[1]] = [p]
                elif p[1] is not None and p[1] in train_data_dict:
                    train_data_dict[p[1]] += [p]
            # 
            for key in train_data_dict.keys():
                if len(train_data_dict[key]) <= chop_threshold:
                    train_data += train_data_dict[key]
                else:
                    train_data += random.sample(train_data_dict[key], chop_threshold)
            del train_data_dict
        del train_data_mapping
        gc.collect()

        print("Data Balancing complete, Start cleaning data.")
        # Clean Train Data
        train_data_clean = []
        i = 1
        percent = 0
        t1 = time.time()
        total_num = len(train_data)
        for p in train_data:
            train_data_clean.append([clean_train(p[0]), p[1]])
            # print process bar
            if i >= total_num * percent:
                percent += 0.01
                t2 = time.time()
                print("[", i, "/", total_num, "]", int(percent * 100), "%", " Estimated time remaining:", 
                      int(((t2 - t1) / i) * (total_num - i + 1)), "s")
            i += 1
        del train_data
        gc.collect()
        t2 = time.time()
        print("Training data cleaned complete, Actual processing time: ", 
              int(t2 - t1), "s, start output data to csv file.")

        # Loop filling
        if loop_filling is True:
            train_data_clean_dict = {}
            for p in train_data_clean:
                if p[1] not in train_data_clean_dict:
                    train_data_clean_dict[p[1]] = [p]
                else:
                    train_data_clean_dict[p[1]] += [p]
            del train_data_clean
            train_data_clean = []
            for key in train_data_clean_dict.keys():
                if len(train_data_clean_dict[key]) >= chop_threshold:
                    train_data_clean += train_data_clean_dict[key]
                else:
                    while len(train_data_clean_dict[key]) < chop_threshold:
                        train_data_clean_dict[key] += train_data_clean_dict[key]
                    train_data_clean += train_data_clean_dict[key][:chop_threshold]
            del train_data_clean_dict
            gc.collect()
            print("Loop Filling Completed")

        # Write to CSV file
        with open(csv_output_path, 'a', newline='', encoding='utf-8') as csv1:
            csv_write = csv.writer(csv1, dialect='excel')
            for p in train_data_clean:
                csv_write.writerow(p)
        print("Data output complete.")


if __name__ == "__main__":
    # ================================================
    # Area: argsparse
    # ================================================
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help="csv input path", required=True)
    parser.add_argument("-o", help="csv output path", required=True)
    parser.add_argument("-s", help="data source", required=True)
    parser.add_argument("-t", help="chop_threshold, 0 = unlimite", type=int, default=0)
    parser.add_argument("-r", help="random sampling in balancing", action='store_true')
    parser.add_argument("-f", help="loop filling", action='store_true')
    parser.add_argument("-c", help="csv mapping table", default="mapping.csv")
    parser.add_argument("-m", help="category miss analysis", nargs="?", const="category_miss.csv")
    parser.add_argument("-n", help="ship mapping", action='store_true')
    args = parser.parse_args()

    csv_input_path = args.i
    csv_output_path = args.o
    chop_threshold = args.t
    random_mode = args.r
    loop_filling = args.f
    mapping_csv_path = args.c
    category_miss_path = args.m
    data_source = args.s
    ship_mapping = args.n
    if data_source == "s":
        pre_processing()
    elif data_source == "r":
    #
    else:
        print("Error, invaild Data Source, please checkout -s option")
        input()
        exit()
