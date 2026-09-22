import os

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from services.queue import publish_message

from database.db import get_connection

from config import Config

from services.cache import (
    redis_client,
    get_cache,
    set_cache,
    delete_cache
)


SERVER_ID = os.getenv("SERVER_ID", "LOCAL")


app = Flask(__name__)

app.config.from_object(Config)




@app.route("/")
def home():

    return render_template(
        "index.html",
        user=get_current_user()
    )


@app.route("/movies")
def movies_page():

    return render_template(
        "movies.html",
        user=get_current_user()
    )


@app.route("/api/server")
def server_identity():

    return jsonify({
        "server": SERVER_ID,
        "message": "Request handled by StreamFlix backend"
    })


@app.route("/api/movies")
def get_movies():

    cache_key = "movies:all"

    # ========================================================
    # CHECK REDIS
    # ========================================================

    cached_movies = get_cache(cache_key)

    if cached_movies is not None:

        return jsonify({

            "source": "redis",

            "server": SERVER_ID,

            "movies": cached_movies

        })


    # ========================================================
    # CACHE MISS -> MYSQL
    # ========================================================

    connection = None

    cursor = None


    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id,
                title,
                genre,
                release_year AS year,
                description
            FROM movies
            ORDER BY id
            """
        )


        movies = cursor.fetchall()


        # ====================================================
        # SAVE RESULT TO REDIS
        # ====================================================

        set_cache(

            cache_key,

            movies,

            expiration=60

        )


        return jsonify({

            "source": "mysql",

            "server": SERVER_ID,

            "movies": movies

        })


    except Exception as error:

        print(
            "Movie database error:",
            error
        )


        return jsonify({

            "error": "Unable to fetch movies"

        }), 500


    finally:

        if cursor:

            cursor.close()


        if connection:

            connection.close()


@app.route("/api/cache")
def cache_status():

    try:

        keys = redis_client.keys("*")

        return jsonify({

            "redis": "connected",

            "keys": keys

        })

    except Exception as error:

        return jsonify({

            "redis": "disconnected",

            "error": str(error)

        }), 503


@app.route("/api/cache/clear")
def clear_cache():

    delete_cache("movies:all")

    return jsonify({

        "message": "Movie cache cleared",

        "server": SERVER_ID

    })


@app.route("/api/movies/<int:movie_id>")
def get_movie(movie_id):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                title,
                genre,
                release_year AS year,
                description
            FROM movies
            WHERE id = %s
            """,
            (movie_id,)
        )

        movie = cursor.fetchone()

        if movie is None:

            return jsonify({
                "error": "Movie not found"
            }), 404

        return jsonify(movie)

    except Exception as error:

        print("Movie database error:", error)

        return jsonify({
            "error": "Unable to fetch movie"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template(
            "register.html",
            user=get_current_user()
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    if not name or not email or not password:

        return render_template(
            "register.html",
            error="All fields are required.",
            user=None
        )

    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters.",
            user=None
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            return render_template(
                "register.html",
                error="An account with this email already exists.",
                user=None
            )

        password_hash = generate_password_hash(
            password
        )

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()

        return redirect(
            url_for("login")
        )

    except Exception as error:

        print("Registration error:", error)

        return render_template(
            "register.html",
            error="Registration failed. Check the server terminal.",
            user=None
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template(
            "login.html",
            user=get_current_user()
        )

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            return render_template(
                "login.html",
                error="Invalid email or password.",
                user=None
            )

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            return render_template(
                "login.html",
                error="Invalid email or password.",
                user=None
            )

        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        return redirect(
            url_for("home")
        )

    except Exception as error:

        print("Login error:", error)

        return render_template(
            "login.html",
            error="Login failed. Check the server terminal.",
            user=None
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


@app.route("/api/me")
def current_user():

    user = get_current_user()

    if user is None:

        return jsonify({
            "authenticated": False
        })

    return jsonify({
        "authenticated": True,
        "user": user
    })



@app.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json(silent=True) or {}

    job = {
        "type": data.get("type", "test"),
        "message": data.get("message", "Hello from StreamFlix"),
        "movie_id": data.get("movie_id"),
        "server": SERVER_ID
    }

    publish_message("streamflix_jobs", job)

    return jsonify({
        "status": "queued",
        "server": SERVER_ID,
        "job": job
    }), 202


@app.route("/health")
def health():

    connection = None

    try:

        connection = get_connection()

        connection.close()

        return jsonify({
            "status": "healthy",
            "server": SERVER_ID,
            "database": "connected"
        })

    except Exception as error:

        print("Health check database error:", error)

        return jsonify({
            "status": "unhealthy",
            "server": SERVER_ID,
            "database": "disconnected"
        }), 503


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )





