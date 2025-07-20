import requests
import json

import requests
import json

def generate_description_stream(job_title, job_type, work_mode, industry, experience_level, min_experience, max_experience, country, city):
    user_prompt = f"""
    Job Title: {job_title}
    Job Type: {job_type}
    Work Mode: {work_mode}
    Industry: {industry}
    Experience Level: {experience_level}
    Minimum Experience: {min_experience} years
    Maximum Experience: {max_experience} years
    Location: {city}, {country}
    """

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "recruiter-assistant",   # your custom model here
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True,
        },
        stream=True,
    )

    capturing = False
    bracket_count = 0

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            content = data.get('message', {}).get('content')
            if content:
                for char in content:
                    if char == '{':
                        capturing = True
                        bracket_count = 1
                        print(char, end='', flush=True)
                        continue
                    if capturing:
                        print(char, end='', flush=True)
                        if char == '{':
                            bracket_count += 1
                        elif char == '}':
                            bracket_count -= 1
                            if bracket_count == 0:
                                print()  # Ensure newline after JSON
                                return  # Stop after closing bracket



# Example usage:
generate_description_stream(
    job_title="Software Engineer",
    job_type="Full-time",
    work_mode="Remote",
    industry="Technology",
    experience_level="Mid-Level",
    min_experience="3",
    max_experience="5",
    country="USA",
    city="New York"
)
