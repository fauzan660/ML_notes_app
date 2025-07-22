import subprocess

pyres_function = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\notes\pyres_skill.py"
pyres_venv = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\env3.6new\Scripts\python.exe"

path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\backend\Resume\media\resumes\accountant_resume_fpdbC3G.pdf"
result = subprocess.run(
    [pyres_venv, pyres_function, path],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True  # Equivalent to text=True in 3.7+
)

output = result.stdout.strip()  # "Python,Django,Machine Learning"
skills_list = output.split(",")  # ['Python', 'Django', 'Machine Learning']

print(skills_list)