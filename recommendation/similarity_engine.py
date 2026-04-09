from sklearn.metrics.pairwise import cosine_similarity
from preprocessing.clean_text import clean_text_pipeline
from preprocessing.skill_normalizer import normalize_skills
from recommendation.vectorizer import get_vectorizer

def process_corpus_and_profile(user_profile_text, job_descriptions):
    """
    Takes user profile string and list of job descriptions.
    Cleans, normalizes, vectorizes, and computes similarity scores.
    """
    # Clean job descriptions
    cleaned_jobs = []
    for desc in job_descriptions:
        p_desc = clean_text_pipeline(desc)
        p_desc = normalize_skills(p_desc)
        cleaned_jobs.append(p_desc)

    # Clean user profile
    p_profile = clean_text_pipeline(user_profile_text)
    p_profile = normalize_skills(p_profile)
    
    # Needs at least one job to compare
    if not cleaned_jobs:
        return []

    # Get fitted vectorizer on jobs text
    vectorizer = get_vectorizer(cleaned_jobs)
    
    # Vectorize
    job_matrices = vectorizer.transform(cleaned_jobs)
    profile_matrix = vectorizer.transform([p_profile])
    
    # Calculate similarity [1 x N] -> Flatten to 1D array
    scores = cosine_similarity(profile_matrix, job_matrices).flatten()
    
    return scores
