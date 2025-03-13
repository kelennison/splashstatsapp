import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import Plot from 'react-plotly.js';  // Import the Plot component for interactive charts
import './App.css';
import './theme.css'; // Dark mode and theme styles
import logo from './logo_enlarged.png'; // Import the image from src folder

function App() {
  const [players, setPlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState({
    player1: '',
    player2: '',
    player3: '',
    player4: ''
  });
  const [minGames, setMinGames] = useState(0.4); // Default min_games value
  const [chartUrl, setChartUrl] = useState(null);
  const [tableJson, setTableJson] = useState(null); // New state to hold the interactive Plotly table JSON
  const [darkMode, setDarkMode] = useState(true); // Dark mode state

  // Checkbox states for additional players
  const [showPlayer2, setShowPlayer2] = useState(false);
  const [showPlayer3, setShowPlayer3] = useState(false);
  const [showPlayer4, setShowPlayer4] = useState(false);

  // Fetch the list of players from the backend
  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/players`)
      .then((res) => res.json())
      .then((data) => setPlayers(data));
  }, []);

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }, [darkMode]);

  // Prepare options for react-select
  const playerOptions = players.map((p) => ({ value: p, label: p }));

  // Handler for react-select changes
  const handlePlayerSelect = (playerField, selectedOption) => {
    setSelectedPlayers((prev) => ({
      ...prev,
      [playerField]: selectedOption ? selectedOption.value : ''
    }));
  };

  // Handler for slider change to adjust minGames value
  // eslint-disable-next-line
  const handleSliderChange = (e) => {
    setMinGames(parseFloat(e.target.value));
  };
  // eslint-disable-next-line
  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };

  // Update checkbox state and clear the corresponding player if unchecked.
  const handleCheckboxChange = (playerNumber, isChecked) => {
    if (playerNumber === 2) {
      setShowPlayer2(isChecked);
      if (!isChecked) {
        setSelectedPlayers((prev) => ({ ...prev, player2: '' }));
      }
    }
    if (playerNumber === 3) {
      setShowPlayer3(isChecked);
      if (!isChecked) {
        setSelectedPlayers((prev) => ({ ...prev, player3: '' }));
      }
    }
    if (playerNumber === 4) {
      setShowPlayer4(isChecked);
      if (!isChecked) {
        setSelectedPlayers((prev) => ({ ...prev, player4: '' }));
      }
    }
  };

  const darkSelectStyles = {
    control: (provided, state) => ({
      ...provided,
      backgroundColor: '#121212',
      borderColor: state.isFocused ? '#333' : '#666',
      color: '#e0e0e0',
    }),
    menu: (provided) => ({
      ...provided,
      backgroundColor: '#121212',
    }),
    singleValue: (provided) => ({
      ...provided,
      color: '#e0e0e0',
    }),
    placeholder: (provided) => ({
      ...provided,
      color: '#888',
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected ? '#333' : state.isFocused ? '#222' : '#121212',
      color: '#e0e0e0',
      cursor: 'pointer',
    }),
  };

  // Add new state for season type
  const [seasonType, setSeasonType] = useState('regular');
  const[selectedSeason,setSelectedSeason]=useState('2025')
  // Add state for glossary
  const [isGlossaryExpanded, setIsGlossaryExpanded] = useState(false);

  // Update useEffect to include season
  useEffect(() => {
  fetch(`${process.env.REACT_APP_API_URL}/api/players?season=${selectedSeason}&type=${seasonType}`)
    .then((res) => res.json())
    .then((data) => setPlayers(data));
  }, [selectedSeason, seasonType]);  // Add seasonType to dependencies

  // Add new state variable for table expander
  const [tableExpanded, setTableExpanded] = useState(false);

  const generateChart = () => {
    const payload = { 
      ...selectedPlayers, 
      min_games: minGames,
      season: selectedSeason,
      season_type: seasonType
    };

    fetch(`${process.env.REACT_APP_API_URL}/api/radar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

      .then((response) => response.json())
      .then((data) => {
        // Radar chart remains as a static image
        const chartUrl = `data:image/png;base64,${data.chart}`;
        setChartUrl(chartUrl);
        // Set the interactive table JSON from the backend response
        setTableJson(data.table_json);
        setTableExpanded(false);
      })
      .catch((error) => {
        console.error('Error:', error);
        setChartUrl(null);
        setTableJson(null);
      });
  };

  return (
    <div className="App">
      <div className="container" style={{ maxWidth: '800px', width: '100%' }}>

        {/* Header with logo and heading */}
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
          <img src={logo} alt="Logo" style={{ width: '50px', height: 'auto' }} />
          <h1 style={{ fontSize: '3em', margin: 0 }}>SplashStats</h1>
        </span>
        
        {/* Subheading */}
        <h2 style={{ marginTop: '0.5rem', fontSize: '1.5em', fontWeight: 'normal' }}>
          NBA Player Comparison Radar
        </h2>
        
        <div style={{ marginTop: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <label>Season:</label>
            <select 
              value={seasonType} 
              onChange={(e) => setSeasonType(e.target.value)}
              className={darkMode ? 'dark-select' : ''}
              style={{ width: '150px' }}  // Fixed width for consistency
            >
              <option value="regular">Regular Season</option>
              <option value="playoffs">Playoffs</option>
            </select>
            
            <label>Year:</label>
            <select 
              value={selectedSeason} 
              onChange={(e) => setSelectedSeason(e.target.value)}
              className={darkMode ? 'dark-select' : ''}
              style={{ width: '150px' }}  // Fixed width for consistency
            >
              <option value="2023">2022-23</option>
              <option value="2024">2023-24</option>
              <option value="2025">2024-25</option>
            </select>
          </div>
        </div>

        {/* Player 1 is always shown using react-select */}
        <div style={{ marginTop: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Player 1:</label>
          <Select
            name="player1"
            options={playerOptions}
            onChange={(selectedOption) => handlePlayerSelect('player1', selectedOption)}
            placeholder="Select Player"
            isClearable
            styles={darkSelectStyles}
          />
        </div>
        {/* Checkbox to show/hide Player 2 selection */}
        <div style={{ marginTop: '1rem' }}>
          <label>
            <input
              type="checkbox"
              checked={showPlayer2}
              onChange={(e) => handleCheckboxChange(2, e.target.checked)}
            />
            Add Player 2
          </label>
          {showPlayer2 && (
            <div style={{ marginTop: '0.5rem' }}>
              <Select
                name="player2"
                options={playerOptions}
                onChange={(selectedOption) => handlePlayerSelect('player2', selectedOption)}
                placeholder="Select Player"
                isClearable
                styles={darkSelectStyles}
              />
            </div>
          )}
        </div>
        {/* Checkbox to show/hide Player 3 selection */}
        <div style={{ marginTop: '1rem' }}>
          <label>
            <input
              type="checkbox"
              checked={showPlayer3}
              onChange={(e) => handleCheckboxChange(3, e.target.checked)}
            />
            Add Player 3
          </label>
          {showPlayer3 && (
            <div style={{ marginTop: '0.5rem' }}>
              <Select
                name="player3"
                options={playerOptions}
                onChange={(selectedOption) => handlePlayerSelect('player3', selectedOption)}
                placeholder="Select Player"
                isClearable
                styles={darkSelectStyles}
              />
            </div>
          )}
        </div>
        {/* Checkbox to show/hide Player 4 selection */}
        <div style={{ marginTop: '1rem' }}>
          <label>
            <input
              type="checkbox"
              checked={showPlayer4}
              onChange={(e) => handleCheckboxChange(4, e.target.checked)}
            />
            Add Player 4
          </label>
          {showPlayer4 && (
            <div style={{ marginTop: '0.5rem' }}>
              <Select
                name="player4"
                options={playerOptions}
                onChange={(selectedOption) => handlePlayerSelect('player4', selectedOption)}
                placeholder="Select Player"
                isClearable
                styles={darkSelectStyles}
              />
            </div>
          )}
        </div>
        <button onClick={generateChart} style={{ marginTop: '1rem' }}>
          Generate Radar Chart
        </button>
        
        {/* Interactive Plotly Table Section */}
        {tableJson && (
          <div style={{ 
            border: '1px solid #333',
            borderRadius: '5px',
            marginBottom: '1rem'
          }}>
            <button 
              onClick={() => setTableExpanded(!tableExpanded)}
              style={{
                width: '100%',
                padding: '0.75rem',
                background: '#121212',
                border: 'none',
                color: '#e0e0e0',
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <span>Player Stats Table</span>
              <span>{tableExpanded ? '▼' : '▶'}</span>
            </button>
            {tableExpanded && (
              <div style={{ padding: '1rem', background: '#1a1a1a' }}>
                <Plot
                  data={JSON.parse(tableJson).data}
                  layout={JSON.parse(tableJson).layout}
                  config={JSON.parse(tableJson).config}
                  style={{ width: '100%' }}
                  useResizeHandler={true}
                />
              </div>
            )}
          </div>
        )}

        {chartUrl && (
          <div style={{ marginTop: '1rem' }}>
            <img src={chartUrl} alt="Radar Chart" className="chart-img" />
            
            {/* Custom Expander for Glossary */}
            <div style={{ 
              border: '1px solid #333',
              borderRadius: '5px',
              marginTop: '1rem'
            }}>
              <button 
                onClick={() => setIsGlossaryExpanded(!isGlossaryExpanded)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#121212',
                  border: 'none',
                  color: '#e0e0e0',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <span>Glossary</span>
                <span>{isGlossaryExpanded ? '▼' : '▶'}</span>
              </button>
              
              {isGlossaryExpanded && (
                <div style={{ 
                  padding: '1rem',
                  background: '#1a1a1a',
                  borderTop: '1px solid #333'
                }}>
                  <p><strong>Points per Game (PPG):</strong> Average number of points scored by the player in each game.</p>
                  <p><strong>Field Goal Percentage (FG%):</strong> The percentage of successful field goals made by the player.</p>
                  <p><strong>Assists per Game (APG):</strong> Average number of assists made by the player in each game.</p>
                  <p><strong>Rebounds per Game (RPG):</strong> Average number of rebounds grabbed by the player in each game.</p>
                  <p><strong>Steals per Game (SPG):</strong> Average number of steals made by the player in each game.</p>
                  <p><strong>Blocks per Game (BPG):</strong> Average number of shots blocked by the player in each game.</p>
                  <p><strong>3-Point Percentage (3P%):</strong> The percentage of successful 3-point shots made by the player.</p>
                  <p><strong>Free Throw Percentage (FT%):</strong> The percentage of successful free throws made by the player.</p>
                  <p><strong>Turnovers per Game (TO/G):</strong> Average number of turnovers committed by the player in each game.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
