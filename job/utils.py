import csv
import json

from django.conf import settings

BASE_DIR = settings.BASE_DIR

INDUSTRIES_CSV_PATH = f"{BASE_DIR}/job/data/Industries.csv"
CITIES_BY_COUNTRY = f"{BASE_DIR}/job/data/cities_by_country.json"


def load_industries():
    industries = []
    with open(INDUSTRIES_CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            industries.append(row[0])
    return industries


def load_cities_by_country():
    with open(CITIES_BY_COUNTRY, encoding="utf-8") as f:
        return json.load(f)
