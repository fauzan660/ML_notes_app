from pyresparser import ResumeParser


data = ResumeParser(r'c:\Users\fauza\Downloads\Sample Resumes-Handout-1.pdf').get_extracted_data()
print(data['skills'])
