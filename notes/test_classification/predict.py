import subprocess
import json
import os
import tempfile
import sys

def get_class_results_39(uploaded_file):
    python39_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume_Classification\env3.6\Scripts\python.exe"
    script_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\Resume_Classification\class.py"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        # Write the content of uploaded_file (a file-like object)
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    try:
        result = subprocess.run([python39_path, script_path, temp_file_path], check=True) # we are simulating running in cmd python engine.py "//path//"

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error running spaCy model: {e}")
        return None

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# ✅ Only runs if script is called directly
if __name__ == "__main__":
    test_file_path = sys.argv[1]

    # Simulate uploaded_file
    with open(test_file_path, "rb") as f:
        result = get_class_results_39(f)
        print(result)
