from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from pathlib import Path
from rapidfuzz import fuzz


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

    def fuzzy_match(self, resume_skills, job_skill):
        for rs in resume_skills:
            if fuzz.ratio(rs, job_skill) >= 85:
                return True
        return False

    def semantic_match(self, resume_skills, job_skill):
        from sentence_transformers import util
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

        total_possible = len(job_skills) * 2
        final_score = (score / total_possible) * 100 if total_possible else 0

        return {
            "exact_matches": list(matched_exact),
            "fuzzy_matches": list(matched_fuzzy),
            "semantic_matches": list(matched_semantic),
            "missing_skills": list(unmatched_job_skills - matched_fuzzy - matched_semantic),
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


def calculate_experience_fit(job, resume):
    if resume.total_experience is None:
        return None
    if job.min_experience is None and job.max_experience is None:
        return None

    exp = resume.total_experience
    min_exp = job.min_experience or 0
    max_exp = job.max_experience or 100

    if min_exp <= exp <= max_exp:
        return "Perfect Fit"
    elif exp < min_exp:
        return "Underqualified"
    else:
        return "Overqualified"


def calculate_designation_similarity(job_title, resume_designation):
    if not job_title or not resume_designation:
        return None
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([job_title.lower(), resume_designation.lower()])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)


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

    if exp_score == "Perfect Fit":
        summary_parts.append("🎯 Ideal experience level")
    elif exp_score == "Overqualified":
        summary_parts.append("🚀 Senior-level expertise")
    elif exp_score == "Underqualified":
        summary_parts.append("🌱 Growing professional")

    if title_score and title_score >= 70:
        summary_parts.append("🔄 Relevant role background")
    elif title_score and title_score >= 40:
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

    if exp_score == "Perfect Fit":
        reasons.append("Experience level perfectly matches job requirements")
    elif exp_score == "Overqualified":
        reasons.append("Brings senior-level expertise that could mentor others")
    elif exp_score == "Underqualified":
        reasons.append("Eager candidate with growth potential")

    if title_score and title_score >= 70:
        reasons.append("Previous role closely aligns with this position")
    elif title_score and title_score >= 40:
        reasons.append("Background shows relevant transferable experience")

    return reasons[:4]


# -------------------- Main Resume Ranking --------------------
def rank_resume(resume, job):
    score_skills, detailed_skill_info, missing_skills = compute_skill_match_new(
        resume.extracted_resume_skills, job.extracted_skills
    )

    exp_score = calculate_experience_fit(job, resume)
    title_score = calculate_designation_similarity(job.job_title, resume.designation)

    exp_val = 100 if exp_score == "Perfect Fit" else 50 if exp_score in ["Overqualified", "Underqualified"] else 0
    title_val = title_score or 0

    final_score = round((score_skills * 0.5) + (exp_val * 0.3) + (title_val * 0.2), 2)

    fitness_summary = generate_candidate_fitness_summary(detailed_skill_info, exp_score, title_score, score_skills)
    print({
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
)
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


# -------------------- Optional: Access raw match data --------------------
def get_detailed_skill_match(resume_skills, job_skills):
    if not resume_skills or not job_skills:
        return {
            "exact_matches": [],
            "fuzzy_matches": [],
            "semantic_matches": [],
            "missing_skills": job_skills,
            "score_percent": 0
        }

    return skill_matcher.rank_resume(resume_skills, job_skills)
