from ingest import movie_id, person_id, principals, db

# How many movies are in the database?
movie_count = movie_id.count_documents({})
print(f"Total number of movies: {movie_count}")

# List all movies released 1994   
#.find(filter, projection) return original title and start year of movies released in 1994

# list all movies released between 1990 and 2000
#.find(filter, projection) return original title an
movies_1990_2000 = list(movie_id.find({"startYear": {"$gte": "1990", "$lte": "2000"}}, {"originalTitle": 1}))
print(f"Movies released between 1990 and 2000: {len(movies_1990_2000)}")    

# Find the 10 most prolific actors/actresses by number of movie credits

pipeline = [
    # Only actors and actresses
    {
        "$match": {
            "category": {"$in": ["actor", "actress"]}
        }
    },
    # Group by person (nconst) and count appearances
    {
        "$group": {
            "_id": "$nconst",
            "movie_count": {"$sum": 1}
        }
    },
    # Sort descending by count
    {
        "$sort": {"movie_count": -1}
    },
    # Limit to top 10
    {
        "$limit": 10
    },
    # Lookup name from person_id collection
    {
        "$lookup": {
            "from": "person_id",
            "localField": "_id",
            "foreignField": "nconst",
            "as": "person_info"
        }
    },
    # Unwind the person_info array
    {
        "$unwind": "$person_info"
    },
    # Project final output
    {
        "$project": {
            "_id": 0,
            "name": "$person_info.primaryName",
            "movie_count": 1
        }
    }
]

top_actors = list(principals.aggregate(pipeline))

print("\nTop 10 Most Prolific Actors/Actresses:\n")
for actor in top_actors:
    print(f"{actor['name']} - {actor['movie_count']} credits")



###################################################################


#List all movies a given person appeared in, sorted by year.

person_name = "Johnny Depp"  

pipeline = [
    # Step 1: Match the person by name
    {
        "$match": {"primaryName": person_name}
    },

    # Step 2: Join with principals to get movie IDs
    {
        "$lookup": {
            "from": "principals",
            "localField": "nconst",
            "foreignField": "nconst",
            "as": "movie_roles"
        }
    },

    # Step 3: Unwind the movie roles array
    {
        "$unwind": "$movie_roles"
    },

    # Step 4: Join with movie collection to get movie info
    {
        "$lookup": {
            "from": "movie_id",
            "localField": "movie_roles.tconst",
            "foreignField": "tconst",
            "as": "movie_info"
        }
    },

    # Step 5: Unwind movie info
    {
        "$unwind": "$movie_info"
    },

    # Step 6: Project only title + year
    {
        "$project": {
            "_id": 0,
            "title": "$movie_info.originalTitle",
            "year": "$movie_info.startYear"
        }
    },

    # Step 7: Sort by year ascending
    {
        "$sort": {"year": 1}
    }
]

results = list(person_id.aggregate(pipeline))

print(f"\n{person_name} appeared in:")

for movie in results:
    print(movie)

###################################################################

#List all movies directed by a specific director.
director_name = "Martin Scorsese"   # change to any director

pipeline = [
    # Step 1: Find the director by name
    {
        "$match": {"primaryName": director_name}
    },

    # Step 2: Join with principals to get their roles
    {
        "$lookup": {
            "from": "principals",
            "localField": "nconst",
            "foreignField": "nconst",
            "as": "roles"
        }
    },

    # Step 3: Unwind roles array
    {
        "$unwind": "$roles"
    },

    # Step 4: Keep only directing roles
    {
        "$match": {"roles.category": "director"}
    },

    # Step 5: Join with movie collection
    {
        "$lookup": {
            "from": "movie_id",
            "localField": "roles.tconst",
            "foreignField": "tconst",
            "as": "movie_info"
        }
    },

    # Step 6: Unwind movie info
    {
        "$unwind": "$movie_info"
    },

    # Step 7: Show only title and year
    {
        "$project": {
            "_id": 0,
            "title": "$movie_info.originalTitle",
            "year": "$movie_info.startYear"
        }
    },

    # Step 8: Sort by year
    {
        "$sort": {"year": 1}
    }
]

results = list(person_id.aggregate(pipeline))

print(f"\nMovies directed by {director_name}:")

for movie in results:
    print(movie)


#####################################################

# Aggregation pipeline to find most common genre
pipeline = [
    # Step 1: Convert comma-separated string into array
    {
        "$project": {
            "genres_array": {"$split": ["$genres", ","]}
        }
    },
    # Step 2: Unwind the array into separate documents
    {
        "$unwind": "$genres_array"
    },
    # Step 3: Group by genre and count occurrences
    {
        "$group": {
            "_id": "$genres_array",
            "count": {"$sum": 1}
        }
    },
    # Step 4: Sort by count descending
    {
        "$sort": {"count": -1}
    },
    # Step 5: Limit to top 1
    {
        "$limit": 1
    }
]

most_common_genre = list(movie_id.aggregate(pipeline))

print("\nMost common genre:")
print(most_common_genre[0]["_id"], "-", most_common_genre[0]["count"], "movies")


###################################################

#Find all movies that two specific actors both appeared in.

# Example actors
actor1_name = "Leonardo DiCaprio"
actor2_name = "Kate Winslet"

# Find their nconst IDs
actor1 = person_id.find_one({"primaryName": actor1_name})["nconst"]
actor2 = person_id.find_one({"primaryName": actor2_name})["nconst"]

pipeline = [
    # Match principals for either actor
    {
        "$match": {"nconst": {"$in": [actor1, actor2]}}
    },
    # Group by movie (tconst) and count how many of the actors appear
    {
        "$group": {
            "_id": "$tconst",
            "actors_count": {"$sum": 1}
        }
    },
    # Keep only movies where both actors appear
    {
        "$match": {"actors_count": 2}
    },
    # Join with movie collection to get titles
    {
        "$lookup": {
            "from": "movie_id",
            "localField": "_id",
            "foreignField": "tconst",
            "as": "movie_info"
        }
    },
    {"$unwind": "$movie_info"},
    # Project only relevant info
    {
        "$project": {
            "_id": 0,
            "title": "$movie_info.originalTitle",
            "year": "$movie_info.startYear"
        }
    },
    # Sort by year
    {"$sort": {"year": 1}}
]

common_movies = list(principals.aggregate(pipeline))

print(f"\n{actor1_name} and {actor2_name} are in these movie together: ")

for movie in common_movies:
    print(movie)

print("Does my code reach here?")


# Find all actors who died between 1990-2000 and appeared in an action movie

pipeline = [
    # Step 1: Match persons who died between 1990 and 2000
    {
        "$match": {
            "deathYear": {"$gte": "1995", "$lte": "2000"}
        }
    },

    # Step 2: Join with principals to get their roles
    {
        "$lookup": {
            "from": "principals",
            "localField": "nconst",
            "foreignField": "nconst",
            "as": "roles"
        }
    },

    # Step 3: Unwind roles
    {
        "$unwind": "$roles"
    },

    # Step 4: Keep only acting roles
    {
        "$match": {
            "roles.category": {"$in": ["actor", "actress"]}
        }
    },

    # Step 5: Join with movies to get genre info
    {
        "$lookup": {
            "from": "movie_id",
            "localField": "roles.tconst",
            "foreignField": "tconst",
            "as": "movie_info"
        }
    },

    # Step 6: Unwind movie info
    {
        "$unwind": "$movie_info"
    },

    # Step 7: Keep only action movies
    {
        "$match": {
            "movie_info.genres": {"$regex": "Action", "$options": "i"}
        }
    },

    # Step 8: Group by person to avoid duplicate actor entries
    {
        "$group": {
            "_id": "$nconst",
            "name": {"$first": "$primaryName"},
            "deathYear": {"$first": "$deathYear"},
            "movies": {
                "$push": {
                    "title": "$movie_info.originalTitle",
                    "year": "$movie_info.startYear"
                }
            }
        }
    },

    # Step 9: Sort by name
    {
        "$sort": {"name": 1}
    },

    # Step 10: Clean up output
    {
        "$project": {
            "_id": 0,
            "name": 1,
            "deathYear": 1,
            "movies": 1
        }
    }
]

results = list(person_id.aggregate(pipeline))

print(f"Actors who died between 1990-2000 and appeared in Action movies:\n")
for actor in results:
    print(f"{actor['name']} (died {actor['deathYear']}):")