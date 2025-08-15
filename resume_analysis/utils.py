from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from pathlib import Path
from rapidfuzz import fuzz


# -------------------- CONFIGURATION --------------------
WEIGHTS = {
    "skills": 0.5,       # % weight of skill match
    "experience": 0.3,   # % weight of experience fit
    "title": 0.2         # % weight of job title match
}

# Skill match scoring
SKILL_POINTS = {
    "exact": 2,
    "fuzzy": 1.5,
    "semantic_strong": 1,
    "semantic_weak": 0.5
}

SEMANTIC_STRONG_THRESHOLD = 0.35
SEMANTIC_WEAK_THRESHOLD = 0.25


# -------------------- SkillMatcher Class --------------------
class SkillMatcher:
    def __init__(self, synonyms_csv_path: str):
        from sentence_transformers import SentenceTransformer
        self.synonym_map = self._load_synonyms(synonyms_csv_path)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

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

    def fuzzy_match_score(self, rs, js):
        return fuzz.ratio(rs, js)

    def semantic_match_score(self, rs, js):
        from sentence_transformers import util
        emb_job = self.model.encode(js, convert_to_tensor=True)
        emb_resume = self.model.encode(rs, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(emb_resume, emb_job)
        return cosine_scores.max().item()

    def rank_resume(self, resume_skills, job_skills):
        resume_skills = self.normalize_list(resume_skills)
        job_skills = self.normalize_list(job_skills)

        matched_exact = set(resume_skills) & set(job_skills)
        unmatched_job_skills = set(job_skills) - matched_exact

        score = len(matched_exact) * SKILL_POINTS["exact"]
        matched_fuzzy = set()
        matched_semantic_strong = set()
        matched_semantic_weak = set()

        for js in unmatched_job_skills:
            # Check fuzzy
            if any(self.fuzzy_match_score(rs, js) >= 85 for rs in resume_skills):
                matched_fuzzy.add(js)
                score += SKILL_POINTS["fuzzy"]
                continue

            # Check semantic
            sem_score = self.semantic_match_score(resume_skills, js)
            if sem_score >= SEMANTIC_STRONG_THRESHOLD:
                matched_semantic_strong.add(js)
                score += SKILL_POINTS["semantic_strong"]
            elif sem_score >= SEMANTIC_WEAK_THRESHOLD:
                matched_semantic_weak.add(js)
                score += SKILL_POINTS["semantic_weak"]

        total_possible = len(job_skills) * SKILL_POINTS["exact"]
        final_score = (score / total_possible) * 100 if total_possible else 0

        # Minimum boost if there are matches but score is too low
        if final_score < 40 and (matched_exact or matched_fuzzy or matched_semantic_strong):
            final_score = max(final_score, 40)

        return {
            "exact_matches": list(matched_exact),
            "fuzzy_matches": list(matched_fuzzy),
            "semantic_matches": list(matched_semantic_strong | matched_semantic_weak),
            "missing_skills": list(unmatched_job_skills - matched_fuzzy - matched_semantic_strong - matched_semantic_weak),
            "score_percent": round(final_score, 2)
        }


# -------------------- Initialization --------------------
skill_matcher = SkillMatcher(
    synonyms_csv_path=r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\resume_analysis\csv_files\skills_synonyms.csv"
)


# -------------------- Skill Match Helpers --------------------
def generate_skill_match_summary(skill_result):
    exact = skill_result["exact_matches"]
    fuzzy = skill_result["fuzzy_matches"]
    semantic = skill_result["semantic_matches"]

    summary_parts = []
    if exact:
        summary_parts.append(f"🎯 Perfect matches: {', '.join(exact)}")
    if fuzzy:
        summary_parts.append(f"🔍 Close matches: {', '.join(fuzzy)}")
    if semantic:
        summary_parts.append(f"🧠 Related skills: {', '.join(semantic)}")

    return " | ".join(summary_parts) if summary_parts else "No matching skills found"


def compute_skill_match_new(resume_skills, job_skills):
    if not resume_skills or not job_skills:
        return 0, {
            "total_matched": [],
            "exact_matches": [],
            "fuzzy_matches": [],
            "semantic_matches": [],
            "match_breakdown": "No skills to match"
        }, job_skills

    result = skill_matcher.rank_resume(resume_skills, job_skills)
    all_matched = result["exact_matches"] + result["fuzzy_matches"] + result["semantic_matches"]

    detailed_info = {
        "total_matched": all_matched,
        "exact_matches": result["exact_matches"],
        "fuzzy_matches": result["fuzzy_matches"],
        "semantic_matches": result["semantic_matches"],
        "match_breakdown": generate_skill_match_summary(result)
    }

    return result["score_percent"], detailed_info, result["missing_skills"]


# -------------------- Experience Fit (Soft Scoring) --------------------
def calculate_experience_fit(job, resume):
    if resume.total_experience is None or (job.min_experience is None and job.max_experience is None):
        return None

    exp = resume.total_experience
    min_exp = job.min_experience or 0
    max_exp = job.max_experience or exp  # if no max, assume current exp is max

    if min_exp <= exp <= max_exp:
        return 100  # perfect fit
    elif exp < min_exp:
        gap = min_exp - exp
    else:
        gap = exp - max_exp

    # Reduce score 10% for each year gap, not below 0
    return max(0, 100 - (gap * 10))


# -------------------- Title Similarity (Hybrid) --------------------
def calculate_designation_similarity(job_title, resume_designations):
    if not job_title or not resume_designations:
        return None
    if isinstance(resume_designations, str):
        resume_designations = [resume_designations]

    best_score = 0
    for designation in resume_designations:
        # TF-IDF score
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([job_title.lower(), designation.lower()])
        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

        # Fuzzy score
        fuzzy_score = fuzz.token_set_ratio(job_title, designation)

        best_score = max(best_score, tfidf_score, fuzzy_score)

    return round(best_score, 2)


# -------------------- Fitness Summary --------------------
def generate_candidate_fitness_summary(skill_info, exp_score, title_score, skill_score):
    summary_parts = []

    if skill_score >= 80:
        summary_parts.append("🌟 Excellent skill match")
    elif skill_score >= 60:
        summary_parts.append("✅ Good skill alignment")
    elif skill_score >= 40:
        summary_parts.append("⚡ Moderate skill fit")
    else:
        summary_parts.append("📚 Developing skill set")

    if exp_score is not None:
        if exp_score >= 90:
            summary_parts.append("🎯 Ideal experience level")
        elif exp_score >= 60:
            summary_parts.append("🚀 Strong experience")
        elif exp_score >= 40:
            summary_parts.append("🌱 Growing professional")

    if title_score:
        if title_score >= 70:
            summary_parts.append("🔄 Relevant role background")
        elif title_score >= 40:
            summary_parts.append("🔀 Transferable experience")

    return " • ".join(summary_parts)


def generate_good_fit_reasons(skill_info, exp_score, title_score):
    reasons = []

    if skill_info["exact_matches"]:
        reasons.append(f"Has {len(skill_info['exact_matches'])} exact skill matches: {', '.join(skill_info['exact_matches'][:3])}")
    if skill_info["fuzzy_matches"]:
        reasons.append(f"Demonstrates {len(skill_info['fuzzy_matches'])} closely related skills")
    if skill_info["semantic_matches"]:
        reasons.append(f"Shows {len(skill_info['semantic_matches'])} complementary technical abilities")

    if exp_score is not None:
        if exp_score >= 90:
            reasons.append("Experience level perfectly matches job requirements")
        elif exp_score >= 60:
            reasons.append("Brings strong professional experience")
        elif exp_score >= 40:
            reasons.append("Eager candidate with growth potential")

    if title_score:
        if title_score >= 70:
            reasons.append("Previous role closely aligns with this position")
        elif title_score >= 40:
            reasons.append("Background shows relevant transferable experience")

    return reasons[:4]


# -------------------- Main Resume Ranking --------------------
def rank_resume(resume, job):
    score_skills, detailed_skill_info, missing_skills = compute_skill_match_new(
        resume.extracted_resume_skills, job.extracted_skills
    )

    exp_score = calculate_experience_fit(job, resume)
    title_score = calculate_designation_similarity(job.job_title, resume.designation)

    exp_val = exp_score or 0
    title_val = title_score or 0

    final_score = round(
        (score_skills * WEIGHTS["skills"]) +
        (exp_val * WEIGHTS["experience"]) +
        (title_val * WEIGHTS["title"]),
        2
    )

    # Apply small boost if there are strong skill matches but final score is too low
    if score_skills >= 60 and final_score < 50:
        final_score = max(final_score, 50)

    fitness_summary = generate_candidate_fitness_summary(detailed_skill_info, exp_score, title_score, score_skills)

    return {
        "resume_id": resume.id,
        "name": resume.name,
        "email": resume.email,
        "skills": resume.extracted_resume_skills,
        "final_score": final_score,
        "skill_score": score_skills,
        "matched_skills": detailed_skill_info["total_matched"],
        "missing_skills": missing_skills,
        "exp_score": exp_score,
        "title_score": title_score,
        "total_experience": resume.total_experience,
        "designation": resume.designation,
        "company_names": resume.company_names,
        "college_name": resume.college_name,
        "skill_details": detailed_skill_info,
        "fitness_summary": fitness_summary,
        "why_good_fit": generate_good_fit_reasons(detailed_skill_info, exp_score, title_score)
    }
