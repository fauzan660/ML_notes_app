import csv
from pathlib import Path
from rapidfuzz import fuzz
import os
from sentence_transformers import SentenceTransformer, util
import json

# Absolute path to your project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the locally downloaded model
MODEL_PATH = os.path.join(BASE_DIR, 'my_local_model')

# Load model once at global scope
model = SentenceTransformer(MODEL_PATH)

class SkillMatcher:
    def __init__(self, synonyms_csv_path: str):
        self.synonym_map = self._load_synonyms(synonyms_csv_path)
        self.model = model

    def _load_synonyms(self, path):
        synonym_map = {}
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                synonym_map[row["alias"].strip().lower()] = row["standard"].strip().lower()
        return synonym_map

    def normalize(self, skill):
        skill = skill.lower().strip()
        return self.synonym_map.get(skill, skill)

    def normalize_list(self, skills):
        return list({self.normalize(skill) for skill in skills})

    def fuzzy_match(self, resume_skills, job_skill):
        for rs in resume_skills:
            if fuzz.ratio(rs, job_skill) >= 85:
                return True
        return False

    def semantic_match(self, resume_skills, job_skill):
        emb_job = self.model.encode(job_skill, convert_to_tensor=True)
        emb_resume = self.model.encode(resume_skills, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(emb_resume, emb_job)
        return cosine_scores.max().item() > 0.35

    def rank_resume(self, resume_skills, job_skills):
        resume_skills = self.normalize_list(resume_skills)
        job_skills = self.normalize_list(job_skills)

        matched_exact = set(resume_skills) & set(job_skills)
        unmatched_job_skills = set(job_skills) - matched_exact

        score = len(matched_exact) * 2
        matched_fuzzy = set()
        matched_semantic = set()

        for js in unmatched_job_skills:
            if self.fuzzy_match(resume_skills, js):
                matched_fuzzy.add(js)
                score += 1
            elif self.semantic_match(resume_skills, js):
                matched_semantic.add(js)
                score += 0.5

        total_possible = len(job_skills) * 2  # Max points per skill is 2 (exact match)
        final_score = (score / total_possible) * 100 if total_possible else 0

        return {
            "exact_matches": list(matched_exact),
            "fuzzy_matches": list(matched_fuzzy),
            "semantic_matches": list(matched_semantic),
            "missing_skills": list(unmatched_job_skills - matched_fuzzy - matched_semantic),
            "score_percent": round(final_score, 2)
        }


def pred(resume_skills, job_skills):

    matcher = SkillMatcher(synonyms_csv_path=r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\resume_analysis\csv_files\skills_synonyms.csv")


    result = matcher.rank_resume(resume_skills, job_skills)

    return result
