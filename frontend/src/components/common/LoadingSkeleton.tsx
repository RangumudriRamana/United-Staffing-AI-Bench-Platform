import React from 'react';
import { Skeleton, Box } from '@mui/material';

interface LoadingSkeletonProps {
  rows?: number;
  height?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ rows = 5, height = 50 }) => {
  return (
    <Box width="100%" display="flex" flexDirection="column" gap={1.5}>
      {Array.from(new Array(rows)).map((_, index) => (
        <Skeleton key={index} variant="rectangular" width="100%" height={height} style={{ borderRadius: 8 }} />
      ))}
    </Box>
  );
};

export default LoadingSkeleton;