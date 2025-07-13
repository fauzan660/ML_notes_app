import subprocess
import json

def pdf_highlight(simple_pdf_path, search_terms_list):
    python39_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\highlight_pdf\env3.9\Scripts\python.exe"
    script_path = r"C:\Users\fauza\OneDrive\Desktop\Resume Folder\highlight_pdf\test.py"

    try:
        result = subprocess.run(
    [python39_path, script_path, "-i", simple_pdf_path, "-a", "Highlight", "-s", *search_terms_list],
    capture_output=True,
    text=True
)

        last_line = result.stdout.strip().split("\n")[-1]
        output_path = json.loads(last_line)["output_file"]
        return output_path
        
        # print("✅ Highlighted file saved at:", output_json)


    except subprocess.CalledProcessError as e:
        print(f"❌ Error running highlight script:\n{e.stderr}")
        return None
