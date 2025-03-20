import React, { useState } from 'react'
import './App.css'

import Gauges from './components/Gauges';
import Alerts from './components/Alerts';
import logo from './assets/logo.png';
import { Grid2, AppBar, Toolbar, Typography, Container, Paper, Tab, Tabs, Grid} from '@mui/material';


function App() {
  const [value, setValue] = useState(0);
  const handleChangeFunc = (event: React.ChangeEvent<{}>, newValue: number) => {
    setValue(newValue);
  }
  return (
        <Grid2 container spacing={0}>
          <Grid2 size={{xs: 12, sm: 12}} minHeight={'70px'} height={'10vh'}>
            <Grid2 container spacing={0}>
              <Grid2 size={{xs: 12, sm: 1.5}}>
                <img src={logo} alt="logo" className="logo"/>
              </Grid2>
              <Grid2 size={{xs: 12, sm: 10.5}} sx={{display: 'flex', alignItems: 'center'}}>
                <Tabs value={value} onChange={handleChangeFunc}>
                  <Tab value={0} label="Soybean" />
                  <Tab value={1} label="Corn" />
                  <Tab value={2} label="Cotton" />
                </Tabs>
              </Grid2>
            </Grid2>
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 8}} height={'90vh'} minHeight={'500px'}>
            <Gauges />
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 4}} height={'90vh'} minHeight={'500px'} overflow={'scroll'}>
            <Alerts />
          </Grid2>
        </Grid2>
  );
}

export default App
