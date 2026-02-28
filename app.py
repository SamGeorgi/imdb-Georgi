from flask import Flask, render_template, request, jsonify
from queries_app import top_actors_query, movies_by_person_query, movies_by_director_query
from ingest import movie_id, person_id, principals

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Endpoint to run queries
@app.route("/run_query", methods=["POST"])
def run_query():
    query_type = request.json.get("query_type")
    parameter = request.json.get("parameter")  # Optional input for name/year, etc.

    try:
        # Reference your existing queries in queries.py
        if query_type == "top_actors":
            results = top_actors_query(principals, person_id)
        elif query_type == "movies_by_person":
            results = movies_by_person_query(parameter, person_id, principals, movie_id)
        elif query_type == "movies_by_director":
            results = movies_by_director_query(parameter, person_id, principals, movie_id)
        else:
            results = []

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)