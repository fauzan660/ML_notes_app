import json 
import requests
import sys
import re
def generate_description(job_title, job_type, work_mode, industry, experience_level, min_experience, max_experience, country, city):
    prompt = (
    f"""
    You are writing realistic and professional job descriptions for recruiters to assist in resume screening and skills extraction.

    You are given the following details to write this job description:
    - Job Title: {job_title}
    - Job Type: {job_type} (e.g., Full-time, Part-time, Contract, Internship)
    - Work Mode: {work_mode} (e.g., Remote, On-site, Hybrid)
    - Industry: {industry}
    - Experience Level: {experience_level}
    - Minimum Experience: {min_experience} years
    - Maximum Experience: {max_experience} years
    - Country: {country}
    - City: {city}

    Instructions:
    1️⃣ Write a **realistic, clear, and concise job description** in **no more than 150 words**.  
    Focus on **key responsibilities, daily tasks, and expectations**.  
    Use **simple, direct, and neutral language. No adjectives, no promotional words.** Mention the work mode (Remote, On-site, Hybrid) in the description if relevant.

    2️⃣ **Separately**, list **5 to 10 core skills or technologies required** for this role in **plain text**, one per line. Prioritize industry-relevant skills based on the job title, industry, and experience level.

    ⛔ Do not include unnecessary information or write extra text.

    ✅ Return the output **strictly as a single JSON string** with **two clear keys only:** """
    )
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
    },
    data=json.dumps({
        "model": "openai/gpt-4o", # Optional
        "max_tokens": 200,
        "messages": [
        {
            "role": "user",
            "content": prompt
        }
        ]
    })
    )
    res = response.json()
    res_entry = res['choices'][0]
    res_data = res_entry['message']['content']
    match = re.search(r'\{.*\}', res_data, re.DOTALL)
    if match:
        cleaned_json = match.group()
    else:
        print("No JSON found")
    
    return cleaned_json
# Example usage
