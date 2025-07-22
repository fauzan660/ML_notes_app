from pyresparser import ResumeParser
import sys


def pyres_skill_extractor(path):
    
    data = ResumeParser(f"{path}").get_extracted_data()
    return data['skills']


if __name__ == "__main__":
    skill_list = pyres_skill_extractor(sys.argv[1])
    print(",".join(skill_list))