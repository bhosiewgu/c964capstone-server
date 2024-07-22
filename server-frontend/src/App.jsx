import { useState, useEffect } from 'react'
import Autocomplete from '@mui/joy/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import Link from '@mui/material/Link';
import Input from '@mui/joy/Input';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { getMovieTitles, getRecommendation } from './routes'

const freshRecommendationsData = { recommendations: [] };

function App() {
  const [movieTitles, setMovieTitles] = useState([])
  const [recommendationsData, setRecommendationsData] = useState(freshRecommendationsData)
  const [isFetching, setIsFetching] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
        setIsFetching(true)
        try {
            const movieTitles = await getMovieTitles();
            movieTitles.sort((a, b) => a.localeCompare(b));
            setMovieTitles(movieTitles)
        } catch (e) {
            setMovieTitles([])
            console.error('error fetching movies', e)
        } finally {
            setIsFetching(false)
        }
    };

    fetchData();
  }, [])

  if (!movieTitles?.length) {
      return null;
  }

  return (
    <>
      <div style={{marginBottom: 100}}>
          <Link
            href={"https://github.com/bhosiewgu/c964capstone-notebook/blob/main/Data%20Transform.ipynb"}
            target={"_blank"}
            rel={"noopener"}
          >
            Jupyter Notebook Results
          </Link>
      </div>
      <div>
        <h1 style={{marginBottom: 0}}>WatchFlicks</h1>
        <h6 style={{marginTop: 10}}>By Brent Hosie</h6>
        <Autocomplete
            disabled={isFetching}
            options={movieTitles}
            placeholder={'Get Recommendations'}
            onChange={(e, newMovieTitle) => {
                if (newMovieTitle) {
                    const fetchData = async () => {
                        setIsFetching(true)
                        try {
                            {/* { recommendations, original_movie_index, original_movie_title } */}
                            const recommendations_data = await getRecommendation(newMovieTitle);
                            setRecommendationsData(recommendations_data);
                        } catch (e) {
                            setRecommendations(freshRecommendationsData)
                            console.error('error fetching recommendation', e)
                        } finally {
                            setIsFetching(false)
                        }
                    };

                    fetchData();
                } else {
                    setRecommendationsData(freshRecommendationsData)
                }
            }}
        />
      </div>
      <div>
          {
              isFetching
              ? (
                  <CircularProgress />
              )
              : (
                  <div>
                      {Boolean(recommendationsData?.recommendations?.length) && (
                          <>
                              <p>
                                  recommendations data for movie index {recommendationsData.original_movie_index}
                              </p>
                              <ul>
                                  {recommendationsData?.recommendations?.map(({title, movie_id, movie_index}, index) => (
                                    <li key={`${title}-${index}`}>{title} (Movie ID: {movie_id}, Movie Index: {movie_index})</li>
                                  ))}
                              </ul>
                          </>
                      )}
                  </div>
              )
          }
      </div>
    </>
  )
}

export default App
