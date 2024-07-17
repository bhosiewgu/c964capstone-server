import { useState, useEffect } from 'react'
import Autocomplete from '@mui/joy/Autocomplete';
import Input from '@mui/joy/Input';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { getMovieTitles, getRecommendation } from './routes'

function App() {
  const [movieTitles, setMovieTitles] = useState([])
  const [recommendations, setRecommendations] = useState([])

  useEffect(() => {
    const fetchData = async () => {
        const movieTitles = await getMovieTitles();
        movieTitles.sort((a, b) => a.localeCompare(b));
        setMovieTitles(movieTitles)
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
            options={movieTitles}
            placeholder={'Get Recommendations'}
            onChange={(e, newValue) => {
                if (newValue) {
                    const fetchData = async () => {
                        const recommendations = await getRecommendation(newValue);
                        setRecommendations(recommendations);
                    };

                    fetchData();
                } else {
                    setRecommendations([])
                }
            }}
        />
      </div>
      <div>
          <ul>
            {recommendations.map((name, index) => (
                <li key={`${name}-${index}`}>{name}</li>
            ))}
          </ul>
      </div>
    </>
  )
}

export default App
