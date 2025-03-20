import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { createTheme } from '@mui/material/styles'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'


const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#80ca3f',
      light: '#7df63c',
      dark: '#274600',
    },
    secondary: {
      main: '#ec3aab',
      light: '#ff99ff',
      dark: '#770087',
    },
    error: {
      main: '#ba2b00',
    },
    warning: {
      main: '#eb8200',
    },
  },
  typography: {
    fontFamily: "Poppins"
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFamily: "Poppins",
        },
      },
    },
  },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
)
