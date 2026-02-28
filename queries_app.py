# queries.py
from ingest import movie_id, person_id, principals

def top_actors_query(principals, person_id):
    pipeline = [
        {"$match": {"category": {"$in": ["actor", "actress"]}}},
        {"$group": {"_id": "$nconst", "movie_count": {"$sum": 1}}},
        {"$sort": {"movie_count": -1}},
        {"$limit": 10},
        {"$lookup": {"from": "person_id", "localField": "_id", "foreignField": "nconst", "as": "person_info"}},
        {"$unwind": "$person_info"},
        {"$project": {"_id": 0, "name": "$person_info.primaryName", "movie_count": 1}}
    ]
    return list(principals.aggregate(pipeline))

def movies_by_person_query(person_name, person_id, principals, movie_id):
    pipeline = [
        {"$match": {"primaryName": person_name}},
        {"$lookup": {"from": "principals", "localField": "nconst", "foreignField": "nconst", "as": "roles"}},
        {"$unwind": "$roles"},
        {"$lookup": {"from": "movie_id", "localField": "roles.tconst", "foreignField": "tconst", "as": "movies_info"}},
        {"$unwind": "$movies_info"},
        {"$project": {"_id": 0, "title": "$movies_info.originalTitle", "year": "$movies_info.startYear"}},
        {"$sort": {"year": 1}}
    ]
    return list(person_id.aggregate(pipeline))

def movies_by_director_query(director_name, person_id, principals, movie_id):
    pipeline = [
        {"$match": {"primaryName": director_name}},
        {"$lookup": {"from": "principals", "localField": "nconst", "foreignField": "nconst", "as": "roles"}},
        {"$unwind": "$roles"},
        {"$match": {"roles.category": "director"}},
        {"$lookup": {"from": "movie_id", "localField": "roles.tconst", "foreignField": "tconst", "as": "movies_info"}},
        {"$unwind": "$movies_info"},
        {"$project": {"_id": 0, "title": "$movies_info.originalTitle", "year": "$movies_info.startYear"}},
        {"$sort": {"year": 1}}
    ]
    return list(person_id.aggregate(pipeline))