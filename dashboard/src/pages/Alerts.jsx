import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  CircularProgress,
  Alert as MuiAlert,
} from '@mui/material'
import axios from 'axios'
import { format } from 'date-fns'

const severityColors = {
  low: 'info',
  medium: 'warning',
  high: 'error',
  critical: 'error',
}

export default function Alerts() {
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('/api/alerts')
      setAlerts(response.data)
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAcknowledge = async (alertId) => {
    try {
      await axios.post(`/api/alerts/${alertId}/acknowledge`)
      // Refresh alerts
      fetchAlerts()
    } catch (error) {
      console.error('Error acknowledging alert:', error)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Alerts & Notifications
      </Typography>

      <Paper sx={{ mt: 3 }}>
        {alerts.length > 0 ? (
          <List>
            {alerts.map((alert) => (
              <ListItem
                key={alert.id}
                sx={{
                  borderBottom: '1px solid #eee',
                  opacity: alert.acknowledged ? 0.6 : 1,
                }}
              >
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1">{alert.title}</Typography>
                      <Chip
                        label={alert.severity}
                        color={severityColors[alert.severity]}
                        size="small"
                      />
                      <Chip label={alert.alert_type} size="small" variant="outlined" />
                      {alert.symbol && (
                        <Chip label={alert.symbol} size="small" variant="outlined" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textPrimary" sx={{ mt: 1 }}>
                        {alert.message}
                      </Typography>
                      <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                        {format(new Date(alert.timestamp), 'MM/dd/yyyy HH:mm:ss')}
                      </Typography>
                      {!alert.acknowledged && (
                        <Button
                          size="small"
                          onClick={() => handleAcknowledge(alert.id)}
                          sx={{ mt: 1 }}
                        >
                          Acknowledge
                        </Button>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Box p={4} textAlign="center">
            <Typography variant="h6" color="textSecondary">
              No alerts
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  )
}