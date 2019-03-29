from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from analyzer import python_analyzer
import numpy as np


class NCutVectorizer(object):
    def __init__(self, analyzer, binary, min_df):
        self.vectorizer = CountVectorizer(analyzer = python_analyzer,
                                          binary=binary,
                                          min_df=min_df)

    def fit_transform(self, docs):
        train_data_features = self.vectorizer.fit_transform(docs)
        train_data_features = train_data_features.toarray()

        # Calculate NCut-weight
        # Fit
        doc_mat_norm = normalize(train_data_features, axis=0)
        S = np.dot(doc_mat_norm.T, doc_mat_norm) + 0.001
        self.D = np.power(np.sum(S, axis=1), -0.5) * np.eye(S.shape[0])

        # Tranform
        Y = np.dot(self.D, train_data_features.T)
        return Y.T

    def get_feature_names(self):
        return self.vectorizer.get_feature_names()

    def transform(object):
        train_data_features = self.vectorizer.transform(docs)
        train_data_features = train_data_features.toarray()
        Y = np.dot(self.D, train_data_features.T)
        return Y.T
