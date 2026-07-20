import React from "react";
import { useQuery } from "@tanstack/react-query";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import { WidgetContainer } from "../components/WidgetContainer";

const fetchRecentActivity = async () => {
  await new Promise((resolve) => setTimeout(resolve, 1400)); // Longer lag to test progressive loading isolation
  return [
    { id: 1, action: "New Submission", desc: "John Doe submitted to Senior React Architect", time: "12m ago" },
    { id: 2, action: "Interview Scheduled", desc: "Jane Smith mapped to United Health Technical Loop", time: "1h ago" },
    { id: 3, action: "Placement Complete", desc: "Robert Lee locked to DevOps Lead contract contract", time: "3h ago" },
  ];
};

export const ActivityWidget: React.FC = () => {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["dashboard", "recentActivity"],
    queryFn: fetchRecentActivity,
  });

  return (
    <WidgetContainer title="Recent Activity Stream" isLoading={isLoading} isError={isError} onRetry={refetch}>
      <List dense disablePadding sx={{ width: "100%" }}>
        {data?.map((act, index) => (
          <React.Fragment key={act.id}>
            <ListItem alignItems="flex-start" sx={{ px: 0, py: 1.5 }}>
              <ListItemText
                primary={<Typography variant="body2" fontWeight="bold">{act.action}</Typography>}
                secondary={
                  <span style={{ display: "flex", justifyContent: "space-between", gap: 8, marginTop: 2 }}>
                    <Typography variant="caption" color="text.secondary">{act.desc}</Typography>
                    <Typography variant="caption" color="text.disabled" sx={{ minWidth: "fit-content" }}>{act.time}</Typography>
                  </span>
                }
              />
            </ListItem>
            {index < data.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </WidgetContainer>
  );
};