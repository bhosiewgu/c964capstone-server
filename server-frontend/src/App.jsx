import { useState, useEffect } from 'react'
import Autocomplete from '@mui/joy/Autocomplete';
import Input from '@mui/joy/Input';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { getMovieTitles, dumpData } from './routes'

function App() {
  const [count, setCount] = useState(0)
  const [movieTitles, setMovieTitles] = useState([])
  useEffect(async() => {
      const movieTitles = await getMovieTitles();
      movieTitles.sort((a, b) => a.localeCompare(b));
      setMovieTitles(movieTitles)
  }, [])
  useEffect(async() => {
      await dumpData();
  }, [])

  return (
    <>
      <div>
        <h1>WatchFlicks</h1>
        <Autocomplete options={movieTitles} placeholder={'Get Recommendations'}/>
      </div>
    </>
  )
}

export default App
