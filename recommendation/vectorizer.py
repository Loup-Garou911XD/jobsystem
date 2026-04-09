from sklearn.feature_extraction.text import TfidfVectorizer

def get_vectorizer(corpus):
    """
    Fits and returns a TF-IDF vectorizer on the given corpus.
    Corpus should be a list of strings (job descriptions).
    """
    # Using english stopwords to filter out common non-informative words
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit the vectorizer on the entire corpus of job descriptions
    if corpus:
        vectorizer.fit(corpus)
    return vectorizer