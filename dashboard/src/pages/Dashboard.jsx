import { useState, useEffect } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import axios from 'axios'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [positions, setPositions] = useState([])
  const [recentTrades, setRecentTrades] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [statsRes, positionsRes, tradesRes] = await Promise.all([
        axios.get('/api/stats/summary'),
        axios.get('/api/positions'),
        axios.get('/api/trades?limit=10'),
      ])

      setStats(statsRes.data)
      setPositions(positionsRes.data)
      setRecentTrades(tradesRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    )
  }

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h5" component="div">
              {value}
            </Typography>
          </Box>
          <Box color={color}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Trades"
            value={stats?.total_trades || 0}
            icon={<ShowChartIcon fontSize="large" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Win Rate"
            value={`${stats?.win_rate || 0}%`}
            icon={<TrendingUpIcon fontSize="large" />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total P&L"
            value={`$${stats?.total_pnl?.toFixed(2) || '0.00'}`}
            icon={
              stats?.total_pnl >= 0 ? (
                <TrendingUpIcon fontSize="large" />
              ) : (
                <TrendingDownIcon fontSize="large" />
              )
            }
            color={stats?.total_pnl >= 0 ? 'success.main' : 'error.main'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Open Positions"
            value={stats?.open_positions_count || 0}
            icon={<AccountBalanceIcon fontSize="large" />}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Open Positions
            </Typography>
            {positions.length > 0 ? (
              positions.map((pos) => (
                <Box key={pos.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                  <Typography variant="subtitle1">{pos.symbol}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Qty: {pos.quantity} @ ${pos.average_entry_price?.toFixed(2)}
                  </Typography>
                  <Typography
                    variant="body2"
                    color={pos.unrealized_pnl >= 0 ? 'success.main' : 'error.main'}
                  >
                    P&L: ${pos.unrealized_pnl?.toFixed(2)} ({
                      pos.unrealized_pnl_percent?.toFixed(2)
                    }%)
                  </Typography>
                </Box>
              ))
            ) : (
              <Typography color="textSecondary">No open positions</Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Trades
            </Typography>
            {recentTrades.length > 0 ? (
              recentTrades.slice(0, 5).map((trade) => (
                <Box key={trade.id} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="subtitle2">
                      {trade.side.toUpperCase()} {trade.symbol}
                    </Typography>
                    <Typography
                      variant="subtitle2"
                      color={trade.side === 'buy' ? 'primary' : 'secondary'}
                    >
                      ${trade.price?.toFixed(2)}
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    {new Date(trade.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              ))
            ) : (
              <Typography color="textSecondary">No recent trades</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}