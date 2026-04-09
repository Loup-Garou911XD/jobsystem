from recommendation.similarity_engine import process_corpus_and_profile

def get_ranked_jobs(user_profile, jobs_list, top_n=10):
    """
    Matches user profile text against jobs list, computes similarity scores,
    and returns ranked top N jobs.
    jobs_list: list of dictionaries, should contain 'id', 'description', etc.
    """
    if not jobs_list:
        return []
        
    descriptions = [job.get('description', '') for job in jobs_list]
    
    # Get scores
    scores = process_corpus_and_profile(user_profile, descriptions)
    
    # Bind scores to jobs
    ranked_jobs = []
    for idx, job in enumerate(jobs_list):
        job_copy = dict(job)
        job_copy['relevance_score'] = round(float(scores[idx]) * 100, 2)
        ranked_jobs.append(job_copy)
        
    # Sort descending by score
    ranked_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return ranked_jobs[:top_n]
