import csv
import time
from pymongo import MongoClient, ASCENDING

# -------------------------
# Config
# -------------------------
MOVIE_TSV = "imdb_assets/title.basics.tsv/title.basics.tsv"
PERSON_TSV = "imdb_assets/name.basics.tsv/name.basics.tsv"
PRINCIPALS_TSV = "imdb_assets/title.principals.tsv/title.principals.tsv"
BULK_SIZE = 1000  # number of documents to insert at a time
DB_NAME = "imdb_database"

# -------------------------
# MongoDB Connection
# -------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]

# -------------------------
# Create collections manually
# -------------------------
movie_id = db["movie_id"]
person_id = db["person_id"]
principals = db["principals"]


# Helper function

def tsv_to_dict(row):
    """Convert TSV row to dict and handle  -> None"""
    return {k: (None if v == r"\N" else v) for k, v in row.items()}

# Load TSV into a collection
def load_tsv_to_collection(collection, tsv_file):
    # Clear old data to make the script safe to re-run
    print(f"[{collection.name}] Clearing existing documents...")
    collection.delete_many({})

    start_time = time.time()
    total_rows = 0
    batch = []

    with open(tsv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            doc = tsv_to_dict(row)
            batch.append(doc)
            total_rows += 1

            if len(batch) >= BULK_SIZE:
                collection.insert_many(batch)
                print(f"[{collection.name}] Inserted {total_rows} rows so far...")
                batch = []

        # Insert any remaining documents
        if batch:
            collection.insert_many(batch)
            print(f"[{collection.name}] Inserted {total_rows} rows total.")

    elapsed = time.time() - start_time
    print(f"[{collection.name}] Finished in {elapsed:.2f} seconds.\n")

# Create indexes
def create_indexes():
    print("Creating indexes...")
    movie_id.create_index([("tconst", ASCENDING)], unique=True)
    person_id.create_index([("nconst", ASCENDING)], unique=True)
    principals.create_index([("tconst", ASCENDING)])
    principals.create_index([("nconst", ASCENDING)])
    print("Indexes created.\n")

# Main
if __name__ == "__main__":
    # Simply load each TSV file, assuming they exist
    load_tsv_to_collection(movie_id, MOVIE_TSV)
    load_tsv_to_collection(person_id, PERSON_TSV)
    load_tsv_to_collection(principals, PRINCIPALS_TSV)

    create_indexes()
    print("Data ingestion complete!")
    print("Total number of movies:", movie_id.count_documents({}))
    print("Total number of persons:", person_id.count_documents({}))
    print("Total number of principals:", principals.count_documents({}))