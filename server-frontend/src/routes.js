import uniq from 'lodash.uniq';

export async function getRecommendation(movieTitle) {
    if (!movieTitle) {
        return Promise.reject('no movie title supplied')
    }

    try {
        const response = await fetch(`/recommendation/${movieTitle}`); // Fetch data from the same server
        const { recommendations } = await response.json();
        return recommendations;
    } catch (error) {
        return Promise.reject(error)
    }
}

export async function getMovieTitles() {
    try {
        const response = await fetch('/get-movie-titles'); // Fetch data from the same server
        const { movie_titles } = await response.json();
        return uniq(movie_titles);
    } catch (error) {
        return Promise.reject(error)
    }
}

export async function dumpData() {
    try {
        const response = await fetch('/dump-data'); // Fetch data from the same server
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        return Promise.reject(error)
    }
}