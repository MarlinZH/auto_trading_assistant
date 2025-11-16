# Trading Dashboard

Real-time web dashboard for monitoring trading bot activity.

## Features

- **Dashboard**: Overview with key metrics and stats
- **Trades**: Complete trade history with filtering
- **Positions**: Real-time position monitoring with P&L
- **Analytics**: Charts and trends (P&L, volume, win rate)
- **Alerts**: Notification center for all bot alerts

## Development

### Install Dependencies

```bash
cd dashboard
npm install
```

### Run Development Server

```bash
npm run dev
```

Dashboard will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## API Configuration

The dashboard expects the Flask API to be running on `http://localhost:5000`. This is configured in `vite.config.js`.

To change the API endpoint, update the proxy configuration:

```js
proxy: {
  '/api': {
    target: 'http://your-api-url:5000',
    changeOrigin: true
  }
}
```

## Technology Stack

- **React 18**: UI framework
- **Material-UI**: Component library
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **React Router**: Navigation
- **Vite**: Build tool

## Pages

### Dashboard (`/`)
Overview with:
- Total trades
- Win rate
- Total P&L
- Open positions count
- Recent trades list
- Open positions list

### Trades (`/trades`)
- Complete trade history
- Filterable table
- Trade details (symbol, side, quantity, price, P&L)

### Positions (`/positions`)
- All open positions
- Real-time P&L
- Entry vs current price
- Auto-refresh every 30 seconds

### Analytics (`/analytics`)
- Daily P&L trend chart
- Trading volume chart
- Win rate trend
- Buy/sell activity

### Alerts (`/alerts`)
- All system alerts
- Severity filtering
- Acknowledge functionality
- Trade alerts, risk alerts, errors

## Deployment

### Static Hosting

1. Build the production bundle:
```bash
npm run build
```

2. Deploy the `dist/` folder to:
   - Netlify
   - Vercel
   - AWS S3 + CloudFront
   - GitHub Pages

### Docker

See `Dockerfile` in project root for containerized deployment.