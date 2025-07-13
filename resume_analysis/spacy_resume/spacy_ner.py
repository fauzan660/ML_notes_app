import subprocess
import json 
import sys
def spacy_ner(text):
    python311_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume_highlight_text\env3.11\Scripts\python.exe"
    script_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume_highlight_text\spacy_ner.py"
    try:
        result = subprocess.run(
            [python311_path, script_path, text],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())  # ← Back to real Python list

    except Exception as e:
        print("Error:", e)
        return None

# Example
if __name__ == "__main__":
    text_to_test = sys.argv[1]

    # Simulate uploaded_file
    result = spacy_ner(text_to_test)
    print(result)