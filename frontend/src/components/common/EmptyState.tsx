import React, { ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';
import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
  icon?: ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'There are no items to display at this moment.',
  actionText,
  onAction,
  icon = <InboxOutlinedIcon sx={{ fontSize: 60, color: 'text.secondary' }} />,
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      p={6}
      textAlign="center"
      bgcolor="background.default"
      borderRadius={2}
      border="1px dashed"
      borderColor="divider"
      my={2}
    >
      <Box mb={2}>{icon}</Box>
      <Typography variant="h6" fontWeight="medium" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" maxWidth="400px" mb={3}>
        {description}
      </Typography>
      {actionText && onAction && (
        <Button variant="contained" color="primary" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;