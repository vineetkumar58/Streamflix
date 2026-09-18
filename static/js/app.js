async function loadMovies() {
    try {
        const response = await fetch("/api/movies");

        if (!response.ok) {
            throw new Error("Failed to load movies");
        }

        const data = await response.json();

        const movies = Array.isArray(data) ? data : data.movies;

        const container = document.getElementById("movies-container");

        if (!container) {
            return;
        }

        container.innerHTML = "";

        movies.forEach(movie => {
            const card = document.createElement("div");
            card.className = "movie-card";

            card.innerHTML = `
                <div class="movie-info">
                    <h3>${movie.title}</h3>
                    <p>${movie.genre || "Unknown genre"}</p>
                    <p>${movie.release_year || ""}</p>
                    <p>${movie.description || ""}</p>
                </div>
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error("Movie loading error:", error);

        const container = document.getElementById("movies-container");

        if (container) {
            container.innerHTML =
                "<p>Unable to load movies.</p>";
        }
    }
}

document.addEventListener("DOMContentLoaded", loadMovies);
