import React from "react";
import Card from "@mui/material/Card";
import CardHeader from "@mui/material/CardHeader";
import CardContent from "@mui/material/CardContent";
import Skeleton from "@mui/material/Skeleton";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

interface WidgetContainerProps {
  title: string;
  isLoading: boolean;
  isError: boolean;
  onRetry?: () => void;
  children: React.ReactNode;
  skeletonHeight?: number;
}

export const WidgetContainer: React.FC<WidgetContainerProps> = ({
  title,
  isLoading,
  isError,
  onRetry,
  children,
  skeletonHeight = 140,
}) => {
  return (
    <Card elevation={2} sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <CardHeader title={<Typography variant="subtitle1" fontWeight="bold">{title}</Typography>} sx={{ pb: 1 }} />
      <CardContent sx={{ flexGrow: 1, pt: 0 }}>
        {isLoading && (
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Skeleton variant="text" width="60%" height={24} />
            <Skeleton variant="rectangular" height={skeletonHeight} sx={{ borderRadius: 1 }} />
          </Box>
        )}

        {isError && !isLoading && (
          <Box sx={{ py: 3, textAlign: "center" }}>
            <Typography variant="body2" color="error" sx={{ mb: 2 }}>
              Failed to refresh metric workspace data stream.
            </Typography>
            {onRetry && (
              <Button size="small" variant="outlined" color="primary" onClick={onRetry}>
                Retry Sync
              </Button>
            )}
          </Box>
        )}

        {!isLoading && !isError && children}
      </CardContent>
    </Card>
  );
};