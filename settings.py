import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

CATEGORIES = ["scientists", "engineers", "entrepreneurs"]

QUANTUM_SCIENTIST_DATABASE_URL = "https://quantumzeitgeist.com/influential-people-in-quantum-computing/"

# global constants for small test dataset that should be removed later
BASE_URL = "https://perimeterinstitute.ca"
PERIMETER_PEOPLE_URL = "https://perimeterinstitute.ca/people"
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_IMAGES_DIR = os.path.join(DATA_DIR, "raw_images")
PROFILES_PATH = os.path.join(DATA_DIR, "profiles.json")
OUT_EMBEDDINGS = os.path.join(DATA_DIR, "embeddings.npy")
OUT_NAMES = os.path.join(DATA_DIR, "names.json")
