import { useState } from 'react'
import './App.css'

import Gauges from './components/Gauges';
import Alerts from './components/Alerts';

import { Grid2, AppBar, Toolbar, Typography, Container, Paper } from '@mui/material';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6">
          My Material UI App
        </Typography>
      </Toolbar>
    </AppBar>
  );
}


function App() {
  return (
    <>
      <Navbar />
      <Container maxWidth={false} sx={{ marginTop: 4 }}>
        <Grid2 container spacing={2}>
          <Grid2 size={{ xs: 12, sm: 8}}>
            <Gauges />
          </Grid2>
          <Grid2 size={{ xs: 12, sm: 4}}>
            <Alerts />
          </Grid2>
        </Grid2>
      </Container>
    </>
  );
}

export default App
