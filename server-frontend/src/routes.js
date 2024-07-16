export async function getRecommendation(movieTitle) {
    if (!movieTitle) {
        return Promise.reject('no movie title supplied')
    }

    try {
        const response = await fetch(`/recommendation/${movieTitle}`); // Fetch data from the same server
        return await response.json();
    } catch (error) {
        return Promise.reject(error)
    }
}

export async function getMovieTitles() {
    console.log('APIURL', API_URL)
    try {
        const response = await fetch('/get-movie-titles'); // Fetch data from the same server
        const { movie_titles } = await response.json();
        return movie_titles;
    } catch (error) {
        return Promise.reject(error)
    }
}