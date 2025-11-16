import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
} from '@mui/material'
import axios from 'axios'
import { format } from 'date-fns'

export default function Trades() {
  const [loading, setLoading] = useState(true)
  const [trades, setTrades] = useState([])

  useEffect(() => {
    fetchTrades()
  }, [])

  const fetchTrades = async () => {
    try {
      const response = await axios.get('/api/trades?limit=100')
      setTrades(response.data)
    } catch (error) {
      console.error('Error fetching trades:', error)
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Trade History
      </Typography>

      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date/Time</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Side</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="right">P&L</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={trade.id}>
                <TableCell>
                  {format(new Date(trade.timestamp), 'MM/dd/yyyy HH:mm:ss')}
                </TableCell>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>
                  <Chip
                    label={trade.side.toUpperCase()}
                    color={trade.side === 'buy' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right">{trade.quantity}</TableCell>
                <TableCell align="right">${trade.price?.toFixed(2)}</TableCell>
                <TableCell align="right">${trade.total_value?.toFixed(2)}</TableCell>
                <TableCell
                  align="right"
                  sx={{
                    color: trade.realized_pnl >= 0 ? 'success.main' : 'error.main',
                  }}
                >
                  ${trade.realized_pnl?.toFixed(2)}
                </TableCell>
                <TableCell>
                  <Chip
                    label={trade.status}
                    color={trade.status === 'executed' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}