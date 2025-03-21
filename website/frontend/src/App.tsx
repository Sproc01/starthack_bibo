import React, { useState, useEffect } from 'react';
import './App.css';

import Gauges from './components/Gauges';
import Alerts from './components/Alerts';
import logo from './assets/logo.png';
import { Grid2, AppBar, Toolbar, Typography, Container, Paper, Tab, Tabs, Grid } from '@mui/material';

function getRandomInt(min: number, max: number) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function App() {
  const [value, setValue] = useState(0);
  const [stress, setStress] = useState([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
  const [labels, setLabels] = useState<string[][]>([[], [], [], [], [], [], [], [], [], [], [], []]);

  const handleChangeFunc = (event: React.ChangeEvent<{}>, newValue: number) => {
    setValue(newValue);
  };

  useEffect(() => {
    const crops = ['soybean', 'corn', 'cotton', 'pippopaperino'];
    const labelsCONST = ["Diurnal Heat", "Frost", "Nightime Heat", "Drought"];

    const fetchData = async () => {
      try {
        let response = await fetch(`https://syngenta-backend.alboracle.duckdns.org/api/predict/temp_stress/${crops[value]}`, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
          let mock_data: number[] = [];
          for (let i = 0; i < 12; i++) {
            mock_data.push(getRandomInt(0, 9));
          }
          setStress(mock_data);
          let mock_labels = [];
          for (let i = 0; i < 12; i++) {
            mock_labels.push(labelsCONST);
          }
          setLabels(mock_labels.map(label => label));
          return;
        }
        let textData = await response.text();
        const parsedData = JSON.parse(textData);

        response = await fetch(`https://syngenta-backend.alboracle.duckdns.org/api/predict/drought_stress`, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        textData = await response.text();
        const droughtData = JSON.parse(textData);

        let new_stress = [];
        let new_labels = [];
        const weeks = Object.keys(parsedData);
        for (let j = 0; j < weeks.length; j++) {
          let key = weeks[j];
          let week_obj = parsedData[key];

          let stress_keys = Object.keys(week_obj);
          let max_val = parseInt(week_obj[stress_keys[0]]);
          for (let i = 1; i < stress_keys.length; i++) {
            let stress_key = stress_keys[i];
            if (week_obj[stress_key] > max_val) {
              max_val = parseInt(week_obj[stress_key]);
            }
          }
          let max_labels_week = [];

          if (droughtData[key] >= max_val && droughtData[key] !== 0) {
            max_val = droughtData[key];
            max_labels_week.push("Drought");
          }

          for (let i = 0; i < stress_keys.length; i++) {
            let stress_key = stress_keys[i];
            if (parseInt(week_obj[stress_key]) === max_val && max_val !== 0) {
              max_labels_week.push(labelsCONST[i]);
            }
          }

          new_stress.push(max_val);
          new_labels.push(max_labels_week);
        }

        setLabels(new_labels);
        setStress(new_stress);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [value]);

  useEffect(() => {
    console.log(stress);
    console.log(labels);
  }, [stress, labels]);

  return (
    <Grid2 container spacing={0}>
      <Grid2 size={{ xs: 12, sm: 12 }} minHeight={'70px'} height={'10vh'}>
        <Grid2 container spacing={0}>
          <Grid2 size={{ xs: 12, sm: 2 }}>
            <img src={logo} alt="logo" className="logo" />
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 10 }} sx={{ display: 'flex', alignItems: 'center' }}>
            <Tabs value={value} onChange={handleChangeFunc}>
              <Tab value={0} label="Soybean" />
              <Tab value={1} label="Corn" />
              <Tab value={2} label="Cotton" />
              <Tab value={3} label="Mock Crop" />
            </Tabs>
          </Grid2>
        </Grid2>
      </Grid2>
      <Grid2 size={{ xs: 12, sm: 8 }} height={'90vh'} minHeight={'500px'}>
        <Gauges stress={stress} />
      </Grid2>
      <Grid2 size={{ xs: 12, sm: 4 }} height={'90vh'} minHeight={'500px'}>
        <Alerts stress={stress} labels={labels} />
      </Grid2>
    </Grid2>
  );
}

export default App;
