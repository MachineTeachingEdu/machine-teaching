import analyzer
#from analyzer import python_analyzer

def create_bag_of_words(docs, vectorizer_method, binary=False, min_df=0.2, vectorizer_params=None):
    if vectorizer_params:
        analyzer.vectorizer_params = vectorizer_params
    vectorizer = vectorizer_method(analyzer = analyzer.python_analyzer,
                                   binary=binary,
                                   min_df=min_df)
    train_data_features = vectorizer.fit_transform(docs)
    try:
        train_data_features = train_data_features.toarray()
    # It's already an array
    except AttributeError:
        pass
    return train_data_features, vectorizer, vectorizer.get_feature_names()

