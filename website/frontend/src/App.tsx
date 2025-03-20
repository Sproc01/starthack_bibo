import React, { useState, useContext, useEffect, createContext } from 'react'
import './App.css'

import Gauges from './components/Gauges';
import Alerts from './components/Alerts';
import logo from './assets/logo.png';
import { Grid2, AppBar, Toolbar, Typography, Container, Paper, Tab, Tabs, Grid} from '@mui/material';


// syngenta-backend.alboracle.duckdns.org
function getRandomInt(min: number,max: number) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}


function App() {
  const [value, setValue] = useState(0);
  const [stress, setStress] = useState([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
  const [labels, setLabels] = useState(['', '', '', '', '', '', '', '', '', '', '', '']);

  const handleChangeFunc = (event: React.ChangeEvent<{}>, newValue: number) => {
    console.log(newValue);
    setValue(newValue);
  }

  useEffect(() => {
    const crops = ['soybean', 'corn', 'cotton'];
    
    // You can use an async function inside useEffect
    const fetchData = async () => {

      
      if(value === 3) {
        let mock_data:number[] = []
        for (let i = 0; i < 12; i++) {
            mock_data.push(getRandomInt(0, 9));
        }
        setStress(mock_data);
        let mock_labels:string[] = []
        for(let i = 0; i < 12; i++) {
          mock_labels.push(crops[getRandomInt(0, 2)]);
        }
        setLabels(mock_labels);
      }
      else {
        
      try {
        const response = await fetch(`https://syngenta-backend.alboracle.duckdns.org/api/predict/temp_stress/${crops[value]}`, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const textData = await response.text();
        // Parse the text data if it's not JSON
        const parsedData = JSON.parse(textData);
        // Update the state with the parsed response
        let new_stress = [];
        let new_labels = [];
        const labels = ["Diurnal", "Frost", "Nightime"]
        const weeks = Object.keys(parsedData);
        for(let j = 0; j < weeks.length; j++) {
          let key = weeks[j];
          let week_obj = parsedData[key];

          let stress_keys = Object.keys(week_obj);
          let max_val = parseInt(week_obj[stress_keys[0]]);
          let max_index = [0];
          for(let i = 1; i < stress_keys.length; i++) {
            let stress_key = stress_keys[i];
            if (week_obj[stress_key] > max_val) {
              max_val = parseInt(week_obj[stress_key]);
              max_index = [i];
            }
            else if (week_obj[stress_key] === max_val) {
              max_index.push(i);
            }
          }

          let risk_str = "";
          for(let i of max_index) {
            risk_str += labels[max_index[i]];
            if (i < max_index.length - 1) {
              risk_str += ", ";
            } 
          }
          new_stress.push(max_val);
          new_labels.push(risk_str);
        }
        setLabels(new_labels);
        setStress(new_stress);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
      }
    };
    
    fetchData();
  }, [value]);

  return (
        <Grid2 container spacing={0}>
          <Grid2 size={{xs: 12, sm: 12}} minHeight={'70px'} height={'10vh'}>
            <Grid2 container spacing={0}>
              <Grid2 size={{xs: 12, sm: 2}}>
                <img src={logo} alt="logo" className="logo"/>
              </Grid2>
              <Grid2 size={{xs: 12, sm: 10}} sx={{display: 'flex', alignItems: 'center'}}>
                <Tabs value={value} onChange={handleChangeFunc}>
                  <Tab value={0} label="Soybean" />
                  <Tab value={1} label="Corn" />
                  <Tab value={2} label="Cotton" />
                  <Tab value={3} label="Mock Crop" />
                </Tabs>
              </Grid2>
            </Grid2>
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 8}} height={'90vh'} minHeight={'500px'}>
            <Gauges stress={stress} labels={labels} />
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 4}} height={'90vh'} minHeight={'500px'} overflow={'scroll'}>
            <Alerts />
          </Grid2>
        </Grid2>
  );
}

export default App;
