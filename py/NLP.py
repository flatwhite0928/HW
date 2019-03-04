
# coding: utf-8

# In[ ]:

import requests
import time
import json
import collections
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import 
from wordcloud import WordCloud
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer
from nltk.tokenize import TreebankWorTokenizer
import re
from sklearn.cross_validation import train_test_split
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import cross_val_score

text1=[]
cate1=[]
offset=0

while True:
    print(offset)
    url = "https://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?offset="+str(offset)
    offset+=20
    params={
        'api-key':'*'
    }
    r = requests.get(url, params=params)
    alls=json.loads(r.text)
    if not alls['results']:
        print('end with', offset)
        break
    for i in range(20):
        cate1.append(alls['results'][i]['section'])
        text1.append(alls['results'][i]['abstract'])
    if offset%400==0:
        time.sleep(3)
        
with open('data.json','w') as f:
    json.dump({'cate':cate1,'text':text1},f,indent=4)


# In[ ]:

name_list = [i for i,j in collections.Counter(c).items()]
num_list = [j for i,j in collections.Counter(c).items()]
    
rects=plt.bar(range(len(num_list)), num_list, color='darkred')
index=[0,1,2,3,4,5]
index=[float(c) for c in index]
plt.ylim(ymax=700, ymin=0)
plt.xticks(index, name_list)
plt.ylabel("count")
for rect in rects:
    height = rect.get_height()+10
    plt.text(rect.get_x() + rect.get_width() / 2, height, str(int(height-10)), ha='center', va='bottom')
plt.show()


# In[ ]:

sw=list(set(stopwords.words('english')))
common_texts = []
for i in x:
    common_texts.append([w for w in i.split(' ') if not w.lower() in sw])
common_dictionary = Dictionary(common_texts)
common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
model = LdaModel(corpus=common_corpus, num_topics=5, id2word=common_dictionary)
output = model.print_topics()


# In[ ]:

wd = WordCloud(background_color='white',

               width=500,height=365,

               margin=2).generate(re)

wd.to_file('art.png')


# In[ ]:

tokenizer = TreebankWordTokenizer()
stemmer = PorterStemmer()

def to_bows(doc):
    tokens = tokenizer.tokenize(doc)
    stemmed_tokens = []
    for token in tokens:
        token = re.sub('[^A-z]', '', token)
        if token:
            stemmed_tokens.append(stemmer.stem(token))
    return collections.Counter(stemmed_tokens)

def tfidf(word_count_df, tf_fun=None, idf_fun=None):
    if not tf_fun:
        tf_fun = lambda x: np.log(1 + x)
    tf_df = word_count_df.apply(tf_fun, axis=1)
    if not idf_fun:
        idf_fun = lambda x: np.log(1 + x.shape[0] / (x > 0).sum())
    idf_df = word_count_df.apply(idf_fun, axis=0)
    idf_df = pd.concat([idf_df] * tf_df.shape[0], axis=1).T
    idf_df.index = tf_df.index
    return tf_df * idf_df

dfs = []
for i in range(len(x)):
    df = pd.DataFrame(to_bows(x[i]),index=[y[i]])
    dfs.append(df)

allx = pd.concat(dfs)
allx.fillna(value=0, inplace=True)
datatd=tfidf(allx)


# In[ ]:

x_train, x_test, y_train, y_test = train_test_split(allx.values, y, test_size=0.2, random_state=42)
results=[]
names=[]
scoring='accuracy'
kfold = model_selection.KFold(n_splits=3, random_state=7)
method=[('RF',RandomForestClassifier(max_depth=80)),('Logistic',LogisticRegression()),
      ( 'svm', svm.SVC(C=0.1, kernel='linear',decision_function_shape='ovr')),
       ('nn',MLPClassifier(solver='adam', alpha=1e-5, hidden_layer_sizes=(50,40,50), random_state=1))]

for m in method:
    cv_results = model_selection.cross_val_score(m[1],x_train, y_train,cv=kfold, scoring=scoring)
    results.append(cv_results)
    names.append(m[0])
    msg = "%s: %f" % (m[0], cv_results.mean())
    print(msg)


# In[ ]:

model3=MLPClassifier(solver='adam', alpha=1e-5, hidden_layer_sizes=(50,40,50), random_state=1)
model3.fit(x_train, y_train)
y_pred = model3.predict(x_test)
nr.append(sklearn.metrics.accuracy_score(np.array(y_test), y_pred, normalize=True, sample_weight=None))
nn.append('nn')

eclf1 = VotingClassifier(estimators=[('svm', model), ('log', model4)], voting='hard') 
# eclf2 = VotingClassifier(estimators=[('svm', model), ('log', model4), ('nn', model3)],voting='soft', weights=[2,2,1]) 
eclf1.fit(x_train, y_train)
y_pred = eclf1.predict(x_test)
sklearn.metrics.accuracy_score(np.array(y_test), y_pred, normalize=True, sample_weight=None)
# for clf, label in zip([eclf1,eclf2], ['Ensemble1','Ensemble2']):
# scores = cross_val_score(clf,x_test,y_test,cv=3, scoring='accuracy')
# print(scores.mean(), label)

