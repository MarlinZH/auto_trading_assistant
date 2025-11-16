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
  CircularProgress,
} from '@mui/material'
import axios from 'axios'
import { format } from 'date-fns'

export default function Positions() {
  const [loading, setLoading] = useState(true)
  const [positions, setPositions] = useState([])

  useEffect(() => {
    fetchPositions()
    const interval = setInterval(fetchPositions, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchPositions = async () => {
    try {
      const response = await axios.get('/api/positions')
      setPositions(response.data)
    } catch (error) {
      console.error('Error fetching positions:', error)
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
        Open Positions
      </Typography>

      {positions.length > 0 ? (
        <TableContainer component={Paper} sx={{ mt: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Entry Price</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">P&L</TableCell>
                <TableCell align="right">P&L %</TableCell>
                <TableCell>Opened At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((pos) => (
                <TableRow key={pos.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{pos.symbol}</Typography>
                  </TableCell>
                  <TableCell align="right">{pos.quantity}</TableCell>
                  <TableCell align="right">${pos.average_entry_price?.toFixed(2)}</TableCell>
                  <TableCell align="right">${pos.current_price?.toFixed(2)}</TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color: pos.unrealized_pnl >= 0 ? 'success.main' : 'error.main',
                    }}
                  >
                    ${pos.unrealized_pnl?.toFixed(2)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color: pos.unrealized_pnl >= 0 ? 'success.main' : 'error.main',
                    }}
                  >
                    {pos.unrealized_pnl_percent?.toFixed(2)}%
                  </TableCell>
                  <TableCell>
                    {format(new Date(pos.opened_at), 'MM/dd/yyyy HH:mm')}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Paper sx={{ p: 4, mt: 3, textAlign: 'center' }}>
          <Typography variant="h6" color="textSecondary">
            No open positions
          </Typography>
        </Paper>
      )}
    </Box>
  )
}