from flask import Flask, render_template, jsonify

from database.db import get_connection


SERVER_ID = os.getenv("SERVER_ID", "LOCAL")

app = Flask(__name__)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# GET ALL MOVIES
# ==========================================

@app.route("/api/movies")
def get_movies():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                genre,
                release_year AS year,
                description
            FROM movies
            ORDER BY id
        """)

        movies = cursor.fetchall()

        return jsonify(movies)

    except Exception as error:

        print("Database error:", error)

        return jsonify({
            "error": "Unable to fetch movies"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET SINGLE MOVIE
# ==========================================

@app.route("/api/movies/<int:movie_id>")
def get_movie(movie_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                genre,
                release_year AS year,
                description
            FROM movies
            WHERE id = %s
        """, (movie_id,))

        movie = cursor.fetchone()

        if movie is None:

            return jsonify({
                "error": "Movie not found"
            }), 404

        return jsonify(movie)

    except Exception as error:

        print("Database error:", error)

        return jsonify({
            "error": "Unable to fetch movie"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():

    try:

        connection = get_connection()

        connection.close()

        return jsonify({
            "status": "healthy",
            "server": "streamflix-server",
            "database": "connected"
        })

    except Exception as error:

        print("Health check database error:", error)

        return jsonify({
            "status": "unhealthy",
            "server": "streamflix-server",
            "database": "disconnected"
        }), 503


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

