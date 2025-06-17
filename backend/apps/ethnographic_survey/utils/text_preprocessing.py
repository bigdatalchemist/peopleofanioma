from django.shortcuts import render, redirect
from ..models import EthnographicSurvey
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return tokens

def extract_tfidf_keywords(corpus, top_n=20):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([corpus])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()

    keywords = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    return keywords

def perform_topic_modeling(documents, num_topics=5):
    processed_docs = [preprocess_text(doc) for doc in documents]
    dictionary = corpora.Dictionary(processed_docs)
    corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
    lda_model = models.LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, passes=10)

    topics = lda_model.print_topics(num_words=5)
    parsed_topics = []
    for i, topic in topics:
        topic_keywords = topic.split(" + ")
        keywords = [word.split("*")[1].strip('"') for word in topic_keywords]
        parsed_topics.append({"topic_num": i + 1, "keywords": keywords})
    return parsed_topics
