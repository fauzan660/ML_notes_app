import numpy as np 
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from .preprocessing import preprocess_text
from sklearn.metrics.pairwise import cosine_similarity

def score_calculator(job_description, resume_content):

    df = pd.read_csv("./notes/static/notes/data/UpdatedResumeDataset.csv")


    tf = TfidfVectorizer()
    tfidf_matrix = tf.fit_transform(df['Resume'])


    job_desc = tf.transform([preprocess_text(job_description)]).toarray()
    resume_cont =  tf.transform([preprocess_text(resume_content)]).toarray()

    sim = cosine_similarity(job_desc, resume_cont)[0][0]
    result = 1 + (sim * 4)
    return round(result, 1)