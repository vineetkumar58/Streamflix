console.log("StreamFlix frontend loaded");


async function loadMovies() {

    try {

        const response = await fetch("/api/movies");

        if (!response.ok) {
            throw new Error("Failed to fetch movies");
        }

        const movies = await response.json();

        const movieGrid =
            document.getElementById("movie-grid");

        movieGrid.innerHTML = "";


        movies.forEach(movie => {

            const movieCard =
                document.createElement("div");

            movieCard.className = "movie-card";


            movieCard.innerHTML = `

                <div class="poster">

                    ${movie.title}

                </div>

                <h3>
                    ${movie.title}
                </h3>

                <p class="movie-info">

                    ${movie.genre} • ${movie.year}

                </p>

            `;


            movieGrid.appendChild(movieCard);

        });

    }

    catch (error) {

        console.error(error);

        document.getElementById("movie-grid").innerHTML = `

            <p>
                Failed to load movies.
            </p>

        `;

    }

}


loadMovies();
