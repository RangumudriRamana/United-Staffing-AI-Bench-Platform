import React from "react";
import { useQuery } from "@tanstack/react-query";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import PeopleIcon from "@mui/icons-material/People";
import AssignmentIcon from "@mui/icons-material/Assignment";
import SendIcon from "@mui/icons-material/Send";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import Skeleton from "@mui/material/Skeleton";

// Independent Fetch Hook
const fetchSummaryStats = async () => {
  // TODO: Point directly to backend metrics endpoint when available
  await new Promise((resolve) => setTimeout(resolve, 800)); // Progressive loading simulation
  return { activeConsultants: 42, openRequirements: 18, activeSubmissions: 156, interviewsToday: 5 };
};

export const SummaryCards: React.FC = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["dashboard", "summaryStats"],
    queryFn: fetchSummaryStats,
  });

  const metrics = [
    { label: "Active Consultants", val: data?.activeConsultants, icon: <PeopleIcon color="primary" /> },
    { label: "Open Requirements", val: data?.openRequirements, icon: <AssignmentIcon color="success" /> },
    { label: "Active Submissions", val: data?.activeSubmissions, icon: <SendIcon color="warning" /> },
    { label: "Interviews Today", val: data?.interviewsToday, icon: <CalendarMonthIcon color="error" /> },
  ];

  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Skeleton variant="rectangular" height={90} sx={{ borderRadius: 2 }} />
          </Grid>
        ))}
      </Grid>
    );
  }

  if (isError) {
    return (
      <Paper sx={{ p: 3, textAlign: "center", color: "error.main" }}>
        Error mounting dashboard overview telemetry. <span style={{ cursor: "pointer", textDecoration: "underline" }} onClick={() => refetch()}>Retry</span>
      </Paper>
    );
  }

  return (
    <Grid container spacing={2}>
      {metrics.map((m, idx) => (
        <Grid item xs={12} sm={6} md={3} key={idx}>
          <Paper elevation={2} sx={{ p: 2, display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary" fontWeight="medium">{m.label}</Typography>
              <Typography variant="h4" sx={{ fontWeight: "bold", mt: 0.5 }}>{m.val}</Typography>
            </Box>
            <Box sx={{ p: 1.5, bgcolor: "action.hover", borderRadius: "50%", display: "flex" }}>{m.icon}</Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};