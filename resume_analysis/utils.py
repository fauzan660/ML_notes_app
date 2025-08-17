from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import csv
from pathlib import Path
from rapidfuzz import fuzz
import re
from datetime import datetime, timedelta
import spacy
from collections import Counter
import numpy as np

# Load spaCy model for NER (install with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# -------------------- ENHANCED CONFIGURATION --------------------
WEIGHTS = {
    "skills": 0.45,       # Slightly reduced to balance other factors
    "experience": 0.30,   
    "title": 0.15,        # Reduced for better semantic matching
    "education": 0.05,    # New: education relevance
    "domain": 0.05        # New: domain/industry fit
}

# Enhanced skill match scoring with context awareness
SKILL_POINTS = {
    "exact": 2.0,
    "fuzzy": 1.6,
    "semantic_strong": 1.2,
    "semantic_weak": 0.6,
    "context_boost": 0.3  # Boost for skills found in relevant context
}

# Dynamic thresholds based on skill type
SEMANTIC_THRESHOLDS = {
    "technical": {"strong": 0.4, "weak": 0.28},
    "soft": {"strong": 0.35, "weak": 0.25},
    "domain": {"strong": 0.45, "weak": 0.32},
    "tool": {"strong": 0.5, "weak": 0.35}
}

# Common skill categories for better thresholding
SKILL_CATEGORIES = {
    "technical": ["python", "java", "javascript", "react", "node.js", "sql", "mongodb", 
                 "aws", "docker", "kubernetes", "tensorflow", "pytorch"],
    "soft": ["leadership", "communication", "teamwork", "problem-solving", "management"],
    "domain": ["finance", "healthcare", "retail", "manufacturing", "education"],
    "tool": ["jira", "confluence", "slack", "github", "jenkins", "tableau"]
}
class EnhancedSkillMatcher:
    def __init__(self):  # Remove synonyms_csv_path parameter
        from sentence_transformers import SentenceTransformer
        # Remove synonym loading completely
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Build reverse category mapping
        self.skill_to_category = {}
        for category, skills in SKILL_CATEGORIES.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = category

    # Remove _load_synonyms method completely

    def get_skill_category(self, skill):
        """Determine skill category for dynamic thresholding"""
        skill_lower = skill.lower()
        return self.skill_to_category.get(skill_lower, "technical")

    def get_semantic_threshold(self, skill, strength="strong"):
        """Get dynamic threshold based on skill category"""
        category = self.get_skill_category(skill)
        return SEMANTIC_THRESHOLDS[category][strength]

    def normalize(self, skill):
        # Simple normalization without synonyms
        return skill.lower().strip()

    def normalize_list(self, skills):
        return list({self.normalize(skill) for skill in skills})

    # Rest of methods remain the same...
    def extract_skill_context(self, text, skill, window=50):
        """Extract context around skill mentions for relevance scoring"""
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        contexts = []
        start = 0
        while True:
            pos = text_lower.find(skill_lower, start)
            if pos == -1:
                break
            
            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(skill_lower) + window)
            context = text[context_start:context_end]
            contexts.append(context)
            start = pos + 1
        
        return contexts

    def fuzzy_match_score(self, rs, js):
        return fuzz.ratio(rs, js)

    def semantic_match_score(self, rs, js):
        from sentence_transformers import util
        emb_job = self.model.encode(js, convert_to_tensor=True)
        emb_resume = self.model.encode(rs, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(emb_resume, emb_job)
        return cosine_scores.max().item()

    def rank_resume_enhanced(self, resume_skills, job_skills, resume_text=""):
        """Enhanced ranking with context awareness and dynamic thresholds"""
        resume_skills = self.normalize_list(resume_skills)
        job_skills = self.normalize_list(job_skills)

        matched_exact = set(resume_skills) & set(job_skills)
        unmatched_job_skills = set(job_skills) - matched_exact

        score = len(matched_exact) * SKILL_POINTS["exact"]
        matched_fuzzy = set()
        matched_semantic_strong = set()
        matched_semantic_weak = set()

        for js in unmatched_job_skills:
            # Check fuzzy matches with higher threshold for precision
            fuzzy_matches = [(rs, self.fuzzy_match_score(rs, js)) for rs in resume_skills]
            best_fuzzy = max(fuzzy_matches, key=lambda x: x[1]) if fuzzy_matches else (None, 0)
            
            if best_fuzzy[1] >= 88:
                matched_fuzzy.add(js)
                context_boost = 0
                if resume_text:
                    contexts = self.extract_skill_context(resume_text, js)
                    if any("experience" in ctx.lower() or "project" in ctx.lower() 
                          for ctx in contexts):
                        context_boost = SKILL_POINTS["context_boost"]
                
                score += SKILL_POINTS["fuzzy"] + context_boost
                continue

            # Enhanced semantic matching with dynamic thresholds
            sem_score = self.semantic_match_score(resume_skills, js)
            strong_threshold = self.get_semantic_threshold(js, "strong")
            weak_threshold = self.get_semantic_threshold(js, "weak")
            
            if sem_score >= strong_threshold:
                matched_semantic_strong.add(js)
                score += SKILL_POINTS["semantic_strong"]
            elif sem_score >= weak_threshold:
                matched_semantic_weak.add(js)
                score += SKILL_POINTS["semantic_weak"]

        total_possible = len(job_skills) * SKILL_POINTS["exact"]
        final_score = (score / total_possible) * 100 if total_possible else 0

        # Enhanced minimum boost logic
        strong_matches = len(matched_exact) + len(matched_fuzzy) + len(matched_semantic_strong)
        if strong_matches > 0:
            min_score = min(45, 20 + (strong_matches * 8))
            final_score = max(final_score, min_score)

        return {
            "exact_matches": list(matched_exact),
            "fuzzy_matches": list(matched_fuzzy),
            "semantic_matches": list(matched_semantic_strong | matched_semantic_weak),
            "missing_skills": list(unmatched_job_skills - matched_fuzzy - matched_semantic_strong - matched_semantic_weak),
            "score_percent": round(final_score, 2),
            "match_quality": {
                "exact": len(matched_exact),
                "fuzzy": len(matched_fuzzy),
                "semantic_strong": len(matched_semantic_strong),
                "semantic_weak": len(matched_semantic_weak)
            }
        }

class EnhancedExperienceParser:
    """Robust experience calculation with overlap handling and validation"""
    
    def __init__(self):
        self.month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
            'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
            'nov': 11, 'november': 11, 'dec': 12, 'december': 12
        }
        
        # Enhanced patterns with better context awareness
        self.date_patterns = [
            # Company/Role context patterns (more reliable)
            r'(?:at\s+)?([A-Z][a-zA-Z\s&]+)(?:\s*[-–—]\s*)?(\w{3,9})\s+(\d{4})\s*[-–—]\s*(\w{3,9})\s+(\d{4})',
            r'(?:at\s+)?([A-Z][a-zA-Z\s&]+)(?:\s*[-–—]\s*)?(\w{3,9})\s+(\d{4})\s*[-–—]\s*(Present|Current)',
            
            # Standard date patterns with validation
            r'(\w{3,9})\s+(\d{4})\s*[-–—]\s*(\w{3,9})\s+(\d{4})(?=\s|$|\n)',
            r'(\w{3,9})\s+(\d{4})\s*[-–—]\s*(Present|Current)(?=\s|$|\n)',
            r'(\d{4})\s*[-–—]\s*(\d{4})(?=\s|$|\n)',
            r'(\d{4})\s*[-–—]\s*(Present|Current)(?=\s|$|\n)',
        ]

    def parse_month_year(self, month_str, year_str):
        """Enhanced month-year parsing with validation"""
        try:
            year = int(year_str)
            if year < 1970 or year > datetime.now().year + 1:
                return None
                
            if month_str and month_str.lower() not in ['present', 'current']:
                month = self.month_map.get(month_str.lower()[:3])
                if month:
                    return year + (month - 1) / 12.0
            return year
        except (ValueError, TypeError):
            return None

    def extract_employment_periods(self, text):
        """Extract employment periods with enhanced validation"""
        current_year = datetime.now().year
        periods = []
        
        # Remove common noise patterns
        text = re.sub(r'\b(?:graduated|degree|certification|course)\b.*?\d{4}', '', text, flags=re.IGNORECASE)
        
        for i, pattern in enumerate(self.date_patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    if i in [0, 1]:  # Company context patterns
                        # Skip if match looks like education
                        if any(edu_word in match[0].lower() for edu_word in ['university', 'college', 'school', 'institute']):
                            continue
                        match = match[1:]  # Remove company name
                    
                    if len(match) == 4 and match[2].lower() not in ['present', 'current']:  # Start-End
                        start = self.parse_month_year(match[0], match[1])
                        end = self.parse_month_year(match[2], match[3])
                    elif len(match) >= 3 and match[-1].lower() in ['present', 'current']:  # Start-Present
                        start = self.parse_month_year(match[0], match[1])
                        end = current_year
                    elif len(match) == 2 and match[1].lower() not in ['present', 'current']:  # Year-Year
                        start = int(match[0]) if match[0].isdigit() else None
                        end = int(match[1]) if match[1].isdigit() else None
                    else:
                        continue
                    
                    if start and end and start <= end and (end - start) <= 15:  # Reasonable duration
                        periods.append((start, end))
                        
                except (ValueError, IndexError, TypeError):
                    continue
        
        return periods

    def merge_overlapping_periods(self, periods):
        """Merge overlapping employment periods"""
        if not periods:
            return []
        
        # Sort by start date
        periods = sorted(set(periods), key=lambda x: x[0])
        merged = [periods[0]]
        
        for current in periods[1:]:
            last = merged[-1]
            
            # Merge if overlap or gap < 6 months (common career transition time)
            if current[0] <= last[1] + 0.5:
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                merged.append(current)
        
        return merged

    def calculate_total_experience(self, text):
        """Calculate total experience with enhanced accuracy"""
        periods = self.extract_employment_periods(text)
        if not periods:
            # Fallback: look for experience statements
            exp_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
                r'(?:experience|exp).*?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
                r'(\d+)\+?\s*(?:years?|yrs?)'
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        exp = float(match.group(1))
                        return min(exp, 40)  # Cap at 40 years
                    except ValueError:
                        continue
            return 0
        
        merged_periods = self.merge_overlapping_periods(periods)
        total = sum(end - start for start, end in merged_periods)
        
        return round(min(total, 40), 1)  # Cap and round


class EnhancedNERExtractor:
    """Enhanced Named Entity Recognition for companies and education"""
    
    def __init__(self):
        self.company_indicators = [
            'inc', 'corp', 'corporation', 'llc', 'ltd', 'limited', 'company', 
            'technologies', 'solutions', 'systems', 'services', 'consulting',
            'group', 'holdings', 'enterprises', 'international', 'global'
        ]
        
        self.education_indicators = [
            'university', 'college', 'institute', 'school', 'academy',
            'bachelor', 'master', 'degree', 'btech', 'mtech', 'mba', 'phd'
        ]

    def extract_companies(self, text):
        """Extract company names using NER and pattern matching"""
        companies = set()
        
        # SpaCy NER extraction
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    companies.add(ent.text.strip())
        
        # Pattern-based extraction
        company_patterns = [
            r'(?:at|with|@)\s+([A-Z][a-zA-Z\s&]+(?:' + '|'.join(self.company_indicators) + r'))',
            r'([A-Z][a-zA-Z\s&]+(?:' + '|'.join(self.company_indicators) + r'))',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})(?=\s*[-–—]\s*(?:Software|Technology|Consulting))'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_match = re.sub(r'^\W+|\W+$', '', match).strip()
                if len(clean_match) > 2 and not any(edu in clean_match.lower() for edu in self.education_indicators):
                    companies.add(clean_match)
        
        return list(companies)[:10]  # Limit to prevent noise

    def extract_education(self, text):
        """Extract education information"""
        education = {}
        
        # Degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|B\.?Tech|M\.?Tech|MBA|B\.?S|M\.?S|B\.?A|M\.?A)\s*(?:of|in|degree)?\s*([A-Za-z\s]+)',
            r'(B\.?E\.?|M\.?E\.?|B\.?Com|M\.?Com)\s*(?:in\s*)?([A-Za-z\s]+)?'
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education['degree'] = match.group(0).strip()
                break
        
        # University patterns
        uni_patterns = [
            r'([A-Z][a-zA-Z\s]+(?:University|College|Institute))',
            r'(?:from|at)\s+([A-Z][a-zA-Z\s]+(?:University|College|Institute))'
        ]
        
        for pattern in uni_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education['institution'] = match.group(1).strip()
                break
        
        return education


class EnhancedTitleMatcher:
    """Semantic title similarity using embeddings and domain knowledge"""
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            self.model = None
        
        # Title hierarchy and similarity mappings
        self.title_hierarchy = {
            'junior': 1, 'associate': 2, 'mid': 3, 'senior': 4, 'lead': 5,
            'principal': 6, 'staff': 6, 'manager': 7, 'director': 8, 'vp': 9, 'chief': 10
        }
        
        self.role_synonyms = {
            'software engineer': ['developer', 'programmer', 'coder', 'software developer'],
            'data scientist': ['data analyst', 'ml engineer', 'ai engineer'],
            'product manager': ['product owner', 'program manager'],
            'devops': ['sre', 'platform engineer', 'infrastructure engineer']
        }

    def normalize_title(self, title):
        """Clean and normalize job titles"""
        if not title:
            return ""
        
        # Remove company names and common noise
        title = re.sub(r'\b(?:at|@|with)\s+[A-Z][a-zA-Z\s&]+', '', title)
        title = re.sub(r'[^\w\s]', ' ', title.lower())
        title = ' '.join(title.split())
        
        return title

    def get_semantic_similarity(self, title1, title2):
        """Calculate semantic similarity using sentence transformers"""
        if not self.model:
            return 0
        
        try:
            from sentence_transformers import util
            emb1 = self.model.encode(title1)
            emb2 = self.model.encode(title2)
            similarity = util.cos_sim(emb1, emb2)[0][0].item()
            return similarity * 100
        except:
            return 0

    def calculate_title_similarity(self, job_title, resume_titles):
        """Enhanced title similarity with semantic understanding"""
        if not job_title or not resume_titles:
            return 0
        
        if isinstance(resume_titles, str):
            resume_titles = [resume_titles]
        
        job_title_norm = self.normalize_title(job_title)
        best_score = 0
        
        for resume_title in resume_titles:
            if not resume_title:
                continue
                
            resume_title_norm = self.normalize_title(resume_title)
            
            # Traditional fuzzy matching
            fuzzy_score = fuzz.token_set_ratio(job_title_norm, resume_title_norm)
            
            # Semantic similarity
            semantic_score = self.get_semantic_similarity(job_title_norm, resume_title_norm)
            
            # Synonym matching
            synonym_score = 0
            for base_role, synonyms in self.role_synonyms.items():
                if base_role in job_title_norm:
                    if any(syn in resume_title_norm for syn in synonyms):
                        synonym_score = 85
                        break
            
            # Combined score with weights
            combined_score = max(
                fuzzy_score * 0.4 + semantic_score * 0.6,
                synonym_score,
                semantic_score
            )
            
            best_score = max(best_score, combined_score)
        
        return round(min(best_score, 100), 2)


# -------------------- ENHANCED MAIN SYSTEM --------------------
class IndustryGradeResumeRanker:
    def __init__(self):  # Remove synonyms_csv_path parameter
        self.skill_matcher = EnhancedSkillMatcher()  # No parameter
        self.experience_parser = EnhancedExperienceParser()
        self.ner_extractor = EnhancedNERExtractor()
        self.title_matcher = EnhancedTitleMatcher()

    def calculate_education_fit(self, job_requirements, resume_education):
        """Calculate education relevance score"""
        # Implement based on your specific needs
        return 75  # Placeholder

    def calculate_domain_fit(self, job_domain, resume_text):
        """Calculate industry/domain fit"""
        # Implement domain matching logic
        return 70  # Placeholder

    def rank_resume(self, resume, job):
        """Industry-grade resume ranking with comprehensive analysis"""
        
        # Enhanced skill matching
        skill_result = self.skill_matcher.rank_resume_enhanced(
            resume.extracted_resume_skills, 
            job.extracted_skills,
            resume.extracted_text
        )
        skill_score = skill_result["score_percent"]
        
        # Enhanced experience calculation
        if not resume.total_experience or resume.total_experience == 0:
            total_exp = self.experience_parser.calculate_total_experience(resume.extracted_text)
        else:
            total_exp = resume.total_experience
        
        # Experience fit scoring
        exp_score = self.calculate_experience_fit(job, total_exp)
        
        # Enhanced title matching
        title_score = self.title_matcher.calculate_title_similarity(
            job.job_title, resume.designation
        )
        
        # New scoring dimensions
        education_score = self.calculate_education_fit(None, None)  # Implement as needed
        domain_score = self.calculate_domain_fit(None, resume.extracted_text)
        
        # Calculate weighted final score
        final_score = (
            skill_score * WEIGHTS["skills"] +
            (exp_score or 0) * WEIGHTS["experience"] +
            (title_score or 0) * WEIGHTS["title"] +
            education_score * WEIGHTS["education"] +
            domain_score * WEIGHTS["domain"]
        )
        
        # Apply intelligent score adjustments
        final_score = self.apply_score_adjustments(
            final_score, skill_result, exp_score, title_score
        )
        
        return {
            "resume_id": resume.id,
            "name": resume.name,
            "email": resume.email,
            "final_score": round(final_score, 2),
            "skill_score": skill_score,
            "exp_score": exp_score,
            "title_score": title_score,
            "education_score": education_score,
            "domain_score": domain_score,
            "total_experience": total_exp,
            "skill_details": skill_result,
            "match_quality": skill_result.get("match_quality", {}),
            "confidence_level": self.calculate_confidence_level(skill_result, exp_score, title_score)
        }
    
    def calculate_experience_fit(self, job, total_experience):
        """Enhanced experience fit calculation"""
        if total_experience is None:
            return None
        
        min_exp = getattr(job, 'min_experience', None) or 0
        max_exp = getattr(job, 'max_experience', None) or total_experience
        
        if min_exp <= total_experience <= max_exp:
            return 100
        elif total_experience < min_exp:
            # Graduated penalty for under-qualified
            gap = min_exp - total_experience
            if gap <= 1:
                return 85  # Close enough
            elif gap <= 2:
                return 70
            else:
                return max(30, 100 - (gap * 15))
        else:
            # Over-qualified - less penalty than under-qualified
            gap = total_experience - max_exp
            return max(60, 100 - (gap * 5))
    
    def apply_score_adjustments(self, base_score, skill_result, exp_score, title_score):
        """Apply intelligent score adjustments based on match quality"""
        adjusted_score = base_score
        
        # Boost for high-quality matches
        match_quality = skill_result.get("match_quality", {})
        exact_matches = match_quality.get("exact", 0)
        
        if exact_matches >= 5:
            adjusted_score += 5  # Strong skill alignment bonus
        
        # Penalty for complete mismatches
        if skill_result["score_percent"] < 20 and (exp_score or 0) < 40:
            adjusted_score *= 0.8  # Reduce score for poor overall fit
        
        return max(0, min(100, adjusted_score))
    
    def calculate_confidence_level(self, skill_result, exp_score, title_score):
        """Calculate confidence in the ranking decision"""
        factors = [
            skill_result["score_percent"],
            exp_score or 50,
            title_score or 50
        ]
        
        avg_score = sum(factors) / len(factors)
        variance = sum((x - avg_score) ** 2 for x in factors) / len(factors)
        
        # Higher confidence for consistent scores across dimensions
        if variance < 100:  # Low variance
            return "High" if avg_score > 70 else "Medium"
        else:
            return "Low"


# -------------------- Manual checks if pyres fails to extract the text --------------------

def rank_resume_enhanced(resume_instance, job):
    ranker = IndustryGradeResumeRanker()
    result = ranker.rank_resume(resume_instance, job)
    
    # Add these additional fields:
    result.update({
        # Extract company names from resume text
        'company_names': ranker.ner_extractor.extract_companies(resume_instance.extracted_text)[:5],
        
        # Add education info
        'education_info': ranker.ner_extractor.extract_education(resume_instance.extracted_text),
        
        # Add fitness summary (AI-generated)
        'fitness_summary': generate_fitness_summary(result),  # You'll need to implement this
        
        # Ensure all skill details are available
        'skills': resume_instance.extracted_resume_skills or [],
        
        # Add confidence level if not already included
        'confidence_level': result.get('confidence_level', 'Low'),
    })
    
    return result

def generate_fitness_summary(result):
    """Generate a brief AI summary of candidate fit"""
    score = result['final_score']
    skill_matches = len(result['skill_details'].get('exact_matches', []))
    missing_skills = len(result['skill_details'].get('missing_skills', []))
    
    if score >= 70:
        return f"Strong candidate with {skill_matches} perfect skill matches. Minimal training required. Ready for immediate contribution to team projects."
    elif score >= 40:
        return f"Promising candidate with {skill_matches} core skills aligned. {missing_skills} skills gaps identified that can be addressed through targeted training."
    else:
        return f"Entry-level candidate with {missing_skills} significant skill gaps. Would require extensive training program before becoming productive."







# from notes.models import UploadedFiles as U

# from job.models import PostJobModel as P

# resume = U.objects.get(id=39)

# job  = P.objects.get(id=9)

# from resume_analysis.utils import rank_resume_enhanced as r

# result = r(resume, job)