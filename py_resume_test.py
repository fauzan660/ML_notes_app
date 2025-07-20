from pyresparser import ResumeParser


data = ResumeParser(r'c:\Users\fauza\Downloads\accountant_resume.pdf').get_extracted_data()
print(data)
