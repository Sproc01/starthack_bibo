import React, { useState } from 'react';
import { 
  Box, 
  Stack, 
  Snackbar,
  Card
} from '@mui/material';
import NotificationCard from './NotificationCard';

function Alerts() {
    // State for controlling the visibility of the snackbar alert
    const [openSnackbar, setOpenSnackbar] = useState(false);

    const handleCloseSnackbar = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpenSnackbar(false);
    };

    // Sample dialog images for different cards
    const successImages = [
        'https://placehold.co/600x400/4CAF50/FFFFFF.png?text=Success+Image+1',
        'https://placehold.co/600x400/4CAF50/FFFFFF.png?text=Success+Image+2',
        'https://placehold.co/600x400/4CAF50/FFFFFF.png?text=Success+Image+3'
    ];
    
    const errorImages = [
        'https://placehold.co/600x400/F44336/FFFFFF.png?text=Error+Image+1',
        'https://placehold.co/600x400/F44336/FFFFFF.png?text=Error+Image+2'
    ];
    
    const warningImages = [
        'https://placehold.co/600x400/FF9800/FFFFFF.png?text=Warning+Image+1',
        'https://placehold.co/600x400/FF9800/FFFFFF.png?text=Warning+Image+2',
        'https://placehold.co/600x400/FF9800/FFFFFF.png?text=Warning+Image+3',
        'https://placehold.co/600x400/FF9800/FFFFFF.png?text=Warning+Image+4'
    ];

    return (
        <Box sx={{ width: '100%', p: 2 }}>
            <Stack spacing={2}>
                <NotificationCard 
                    severity="success"
                    title="Success"
                    message="This is a success notification — click to see more details!"
                    imageUrl="https://placehold.co/100x150/4CAF50/FFFFFF.png?text=Success"
                    dialogImages={successImages}
                    dialogTitle="Success Details"
                />
                
                <NotificationCard 
                    severity="error"
                    title="Error"
                    message="This is an error notification — click to see more details!"
                    imageUrl="https://placehold.co/100x150/F44336/FFFFFF.png?text=Error"
                    dialogImages={errorImages}
                    dialogTitle="Error Details"
                />
                
                <NotificationCard 
                    severity="warning"
                    title="Warning"
                    message="This is a warning notification — click to see more details!"
                    imageUrl="https://placehold.co/100x150/FF9800/FFFFFF.png?text=Warning"
                    dialogImages={warningImages}
                    dialogTitle="Warning Details"
                />
                
                <NotificationCard 
                    severity="info"
                    title="Info"
                    message="This is an info notification — check it out!"
                    imageUrl="https://placehold.co/100x150/2196F3/FFFFFF.png?text=Info"
                />
                
                <NotificationCard 
                    severity="success"
                    variant="outlined"
                    message="This is an outlined success notification with a close button."
                    imageUrl="https://placehold.co/100x150/4CAF50/FFFFFF.png?text=Outlined"
                    onClose={() => console.log('Notification closed')}
                />
                
                <NotificationCard 
                    severity="info"
                    variant="filled"
                    message="Click me to show a temporary notification!"
                    imageUrl="https://placehold.co/100x150/2196F3/FFFFFF.png?text=Click"
                    onClick={() => setOpenSnackbar(true)}
                />
            </Stack>
            
            <Snackbar
                open={openSnackbar}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
            >
                <NotificationCard 
                    severity="success"
                    message="This is a temporary notification!"
                    imageUrl="https://placehold.co/60x80/4CAF50/FFFFFF.png?text=Notify"
                    onClose={handleCloseSnackbar}
                />
            </Snackbar>
        </Box>
    );
}

export default Alerts;