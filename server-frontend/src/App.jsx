import { useState, useEffect } from 'react'
import Autocomplete from '@mui/joy/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import Input from '@mui/joy/Input';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { getMovieTitles, getRecommendation } from './routes'

function App() {
  const [movieTitles, setMovieTitles] = useState([])
  const [recommendations, setRecommendations] = useState([])
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
      <div>
        <h1>WatchFlicks</h1>
        <Autocomplete
            disabled={isFetching}
            options={movieTitles}
            placeholder={'Get Recommendations'}
            onChange={(e, newValue) => {
                if (newValue) {
                    const fetchData = async () => {
                        setIsFetching(true)
                        try {
                            const recommendations = await getRecommendation(newValue);
                            setRecommendations(recommendations);
                        } catch (e) {
                            setRecommendations([])
                        } finally {
                            setIsFetching(false)
                        }
                    };

                    fetchData();
                } else {
                    setRecommendations([])
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
                  <ul>
                    {recommendations.map(({title, movie_id}, index) => (
                        <li key={`${title}-${index}`}>{title} (Entity ID: {movie_id})</li>
                    ))}
                  </ul>
              )
          }
      </div>
    </>
  )
}

export default App
