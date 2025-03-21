import React, { useState } from 'react';

import { 
  Box, 
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Button,
  TextField,
} from '@mui/material';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import FlareIcon from '@mui/icons-material/Flare';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import ErrorIcon from '@mui/icons-material/Error';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import {Accordion, AccordionSummary, Typography, AccordionDetails} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import stressBuster1 from '../assets/product_cards/stress_buster_1.png';
import stressBuster2 from '../assets/product_cards/stress_buster_2.jpeg';
import MapComp from './Map';

// import InputBase from '@mui/material/InputBase';
// import Divider from '@mui/material/Divider';
// import MenuIcon from '@mui/icons-material/Menu';
// import SearchIcon from '@mui/icons-material/Search';
// import DirectionsIcon from '@mui/icons-material/Directions';

// function CustomizedInputBase({location}: {location: string}) {
//   return (
//     <Paper
//       component="form"
//       sx={{ p: '2px 4px', display: 'flex', alignItems: 'center', width:'100%'}}
//     >
//       <IconButton sx={{ p: '10px' }} aria-label="menu">
//         <MenuIcon />
//       </IconButton>
//       <InputBase
//         sx={{ ml: 1, flex: 1 }}
//         placeholder="Search Google Maps"
//         value={location}
//         inputProps={{ 'aria-label': 'search google maps' }}
//       />
//       <IconButton type="button" sx={{ p: '10px' }} aria-label="search">
//         <SearchIcon />
//       </IconButton>
//       <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />
//       <IconButton color="primary" sx={{ p: '10px' }} aria-label="directions">
//         <DirectionsIcon />
//       </IconButton>
//     </Paper>
//   );
// }


function addDays(date:Date, days:number) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

function StressAccordion({id, labels, stress}: { id: number, labels: string[][], stress: number[] }) {
    const [openDialog, setOpenDialog] = useState(false);

    function toggleDialog() {
        setOpenDialog(!openDialog);
    }

    let labelsCONST = ["Diurnal Heat", "Frost", "Nightime Heat", "Drought"]
    const icons = [<LocalFireDepartmentIcon />, <AcUnitIcon />, <DarkModeIcon />, <FlareIcon />]
    let title = "Stress Alerts";
    let icon = <ErrorIcon color="error" />;
    let threshold = [6, 10];
    if(id === 0) {
        title = "Normal Conditions";
        icon = <CheckCircleIcon color="success" />
    }
    else if(id === 1) {
        title = "Stress Warnings";
        icon = <ReportProblemIcon  color="warning"/>
        threshold=[3, 6];
    }

    let labels_dict: { [key: string]: string[] } = {
        "Diurnal Heat": [],
        "Frost": [],
        "Nightime Heat": [],
        "Drought": []
    }

    const curr = new Date(); // get current date

    let stress_items = labelsCONST.filter((label, index) => {
        let flag = false;
        labels.forEach((lab, week) => {
            if(lab.includes(label) && stress[week] >= threshold[0] && stress[week] < threshold[1]) {
                flag = true;
                const week_day = addDays(curr, week*7);
                const last_week_day = addDays(week_day, 6);
                labels_dict[label].push(`${week_day.getDate()}/${week_day.getMonth()} - ${last_week_day.getDate()}/${last_week_day.getMonth()}`);
            }
        });
        return flag;
    }).map((label, index) => {
        return <ListItemButton onClick={toggleDialog} key={index}>
            <ListItemIcon>
                {icons[index]}
            </ListItemIcon>
            <ListItemText primary={label + ": "} secondary={labels_dict[label].join(', ')} />
            <Dialog open={openDialog}
                onClose={toggleDialog}
                maxWidth="md"
                fullWidth>
                <DialogTitle>
                {"STRESS BUSTER"}
                <IconButton
                    aria-label="close"
                    onClick={toggleDialog}
                    sx={{
                    position: 'absolute',
                    right: 8,
                    top: 8,
                    }}
                >
                    <CloseIcon />
                </IconButton>
                </DialogTitle>
                <DialogContent dividers>
                <Box sx={{ mt: 2 }}>
                    <Stack spacing={2}>
                        <img src={stressBuster1} />
                        <img src={stressBuster2} />
                    </Stack>
                </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={toggleDialog}>Close</Button>
                </DialogActions>
            </Dialog>
        </ListItemButton>
    }
    );

    return (<Accordion  defaultExpanded = {stress_items.length !== 0} elevation={2}>
        <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls="panel1-content"
        id="panel1-header"
        >
        {icon}
        <Typography component="span" sx={{margin:"0px 0px 0px 10px"}}>{title}</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{padding: 0}}>
        <Typography>
        <List
            sx={{ width: '100%', bgcolor: 'background.paper' }}
            component="nav"
        >
            {stress_items}
        </List>
        </Typography>
        </AccordionDetails>
    </Accordion>
    )
}

function Alerts({stress, labels}: {stress: number[], labels: string[][]}) {
    const [latitude, setLatitude] = useState(-12.524055376770672);
    const [longitude, setLongitude] = useState(-55.69886311374719);
    const [location, setLocation] = useState('Sorriso, State of Mato Grosso, 78890-000, Brazil');

    return (
        <div>
            <div className='geo-map'>
                <MapComp latitude={latitude} longitude={longitude} zoom={13} height={'260px'} width={'260px'} />
                <TextField id="filled-basic" label="Location" color='success' variant="standard" sx={{padding:'6px', width:'100%'}} value={location}/>
            </div>
            <div style={{overflowY: 'auto', height: 'calc(90vh - 352px)'}}>
            {
                [2, 1].map((id) => {
                    return <StressAccordion id={id} labels={labels} stress={stress}/>
                })
            }
            </div>
        </div>
    );
}

// <div className='coordinates'>
//     <TextField id="filled-basic" label="Latitude" color='success' variant="standard" sx={{padding:'6px', width:'100%'}} value={latitude}/>
//     <TextField id="filled-basic" label="Longitude" color='success' variant="standard" sx={{padding:'6px', width:'100%'}} value={longitude}/>
// </div>

export default Alerts;