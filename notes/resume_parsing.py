import subprocess
import json
import os
import tempfile

def get_ner_from_39_env(uploaded_file):  # file from request.FILES["file"]
    python39_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume-Parser-master\Resume-Parser-master\env3.9\Scripts\python.exe"
    script_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume-Parser-master\Resume-Parser-master\src\engine.py"
    output_file = "ner_output.json"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    try:
        # Call the external script using the saved file path
        subprocess.run([python39_path, script_path, temp_file_path], check=True)

        if not os.path.exists(output_file):
            raise FileNotFoundError("NER output file not found")

        with open(output_file, "r") as f:
            result = json.load(f)

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error running spaCy model: {e}")
        return None

    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
