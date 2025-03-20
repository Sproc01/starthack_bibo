import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  CardMedia,
  Typography, 
  IconButton, 
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Paper,
  Stack
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';

type SeverityType = 'success' | 'error' | 'warning' | 'info';
type VariantType = 'bordered' | 'outlined' | 'filled';

interface NotificationCardProps {
  severity: SeverityType;
  title?: string;
  message: string;
  imageUrl?: string;
  dialogImages?: string[];  // New prop for dialog images
  dialogTitle?: string;     // New prop for dialog title
  variant?: VariantType;
  onClick?: () => void;
  onClose?: () => void;
}

const NotificationCard: React.FC<NotificationCardProps> = ({
  severity,
  title,
  message,
  imageUrl,
  dialogImages = [],
  dialogTitle,
  variant = 'bordered',
  onClick,
  onClose
}) => {
  // Add state for dialog
  const [openDialog, setOpenDialog] = useState(false);

  // Map severity to icon and colors
  const getIcon = () => {
    switch (severity) {
      case 'success':
        return <CheckCircleIcon sx={{ color: variant === 'filled' ? 'white' : 'success.main', mr: 2 }} />;
      case 'error':
        return <ErrorIcon sx={{ color: variant === 'filled' ? 'white' : 'error.main', mr: 2 }} />;
      case 'warning':
        return <WarningIcon sx={{ color: variant === 'filled' ? 'white' : 'warning.main', mr: 2 }} />;
      case 'info':
        return <InfoIcon sx={{ color: variant === 'filled' ? 'white' : 'info.main', mr: 2 }} />;
      default:
        return <InfoIcon sx={{ color: variant === 'filled' ? 'white' : 'info.main', mr: 2 }} />;
    }
  };

  // Styles based on variant
  const getCardStyles = () => {
    if (variant === 'filled') {
      return {
        bgcolor: `${severity}.main`,
        color: 'white',
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { boxShadow: 6 } : {}
      };
    } else if (variant === 'outlined') {
      return {
        border: 1,
        borderColor: `${severity}.main`
      };
    } else { // bordered
      return {
        borderLeft: 4,
        borderColor: `${severity}.main`
      };
    }
  };

  const handleCardClick = () => {
    if (dialogImages && dialogImages.length > 0) {
      setOpenDialog(true);
    } else if (onClick) {
      onClick();
    }
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
  };

  return (
    <>
      <Card 
        sx={{ 
          ...getCardStyles(),
          display: 'flex'
        }}
        onClick={handleCardClick}
      >
        {imageUrl && (
          <CardMedia
            component="img"
            sx={{ width: 100, height: '100%', objectFit: 'cover' }}
            image={imageUrl}
            alt={`${severity} notification`}
          />
        )}
        <CardContent sx={{ display: 'flex', alignItems: 'center', p: 2, "&:last-child": { pb: 2 }, flex: 1 }}>
          {getIcon()}
          <Box sx={{ flex: 1 }}>
            {title && (
              <Typography variant="subtitle1" fontWeight="bold">{title}</Typography>
            )}
            <Typography variant="body2">{message}</Typography>
          </Box>
          {onClose && (
            <IconButton
              aria-label="close"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              sx={{ color: variant === 'filled' ? 'white' : 'inherit' }}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          )}
        </CardContent>
      </Card>

      {/* Dialog for showing images */}
      <Dialog
        open={openDialog}
        onClose={handleDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogTitle || title || 'Notification Details'}
          <IconButton
            aria-label="close"
            onClick={handleDialogClose}
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
          {/* <Typography gutterBottom variant="body1">
            {message}
          </Typography> */}
          <Box sx={{ mt: 2 }}>
            <Stack spacing={2}>
              {dialogImages.map((img, index) => (
                <Paper elevation={2} key={index}>
                  <CardMedia
                    component="img"
                    image={img}
                    alt={`Image ${index + 1}`}
                    sx={{
                      width: '100%',
                      maxHeight: 400,
                      objectFit: 'contain',
                      borderRadius: 1
                    }}
                  />
                </Paper>
              ))}
            </Stack>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default NotificationCard;
