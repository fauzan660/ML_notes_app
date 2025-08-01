from pyresparser import ResumeParser
import sys
import json


def pyres_skill_extractor(path):
    data = ResumeParser(path).get_extracted_data()
    return data  # return the full parsed resume dict


if __name__ == "__main__":
    resume_data = pyres_skill_extractor(sys.argv[1])
    print(json.dumps(resume_data, indent=2))  # pretty-print for testing