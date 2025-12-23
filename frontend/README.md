# Predictive Transaction Intelligence - Frontend

React/Next.js frontend application for the BFSI fraud detection system.

## Features

- **Dashboard**: Real-time metrics and statistics
- **Transactions**: Paginated table with detailed transaction data
- **Analytics**: EDA visualizations and insights
- **Upload**: File upload interface for new data

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API Communication**: Fetch API

## Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8001

## Installation

```bash
# Install dependencies
npm install
```

## Configuration

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

This configures the backend API URL. Adjust if your API runs on a different port.

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will start on [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## Backend API Integration

The frontend connects to the Flask API backend. Ensure the backend is running before starting the frontend:

```bash
# In the project root directory
python -m src.api.app --port 8001
```

### API Endpoints Used

- `GET /api/metrics` - Dashboard statistics
- `GET /api/transactions?limit=&offset=` - Paginated transactions
- `GET /api/transactions/sample` - Sample data
- `GET /api/download/processed` - Download CSV

## Setup Chart Images

To display EDA visualizations:

1. Create the charts directory:
```bash
mkdir -p public/assets/charts
```

2. Copy PNG files from the backend:
```bash
# From the project root
cp docs/figs/*.png frontend/public/assets/charts/
```

Or on Windows:
```powershell
Copy-Item docs\figs\*.png frontend\public\assets\charts\
```

The following chart files are needed:
- `fig1_fraud_count.png`
- `fig2_box_amount.png`
- `fig3_heatmap_time.png`
- `fig4_channel_fraud.png`
- `fig5_segment_risk.png`
- `fig6_kyc_impact.png`

## UI Reference Images

Place UI reference images in `public/assets/refs/` to match the design:

```bash
mkdir -p public/assets/refs
# Copy your reference images here
```

The application layout and styling can be customized based on these reference images. Update the Tailwind configuration and component styles as needed.

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Dashboard page
│   ├── transactions/
│   │   └── page.tsx          # Transactions table
│   ├── analytics/
│   │   └── page.tsx          # EDA visualizations
│   ├── upload/
│   │   └── page.tsx          # File upload
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── public/
│   └── assets/
│       ├── charts/           # EDA chart PNGs
│       └── refs/             # UI reference images
├── .env.local                # Environment variables
└── package.json              # Dependencies
```

## Development

### Adding New Pages

Create a new directory under `app/` with a `page.tsx` file:

```tsx
export default function NewPage() {
  return <div>New Page</div>;
}
```

### API Integration

Use the `NEXT_PUBLIC_API_URL` environment variable:

```tsx
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const response = await fetch(`${API_BASE_URL}/api/endpoint`);
```

### Styling

The project uses Tailwind CSS. Add custom classes in `tailwind.config.ts` or use utility classes directly in components.

## Customization for UI Reference Images

When you upload UI reference images:

1. Place images in `public/assets/refs/`
2. Update colors in `tailwind.config.ts`:
```ts
theme: {
  extend: {
    colors: {
      primary: '#your-color',
      secondary: '#your-color',
    }
  }
}
```

3. Adjust component layouts in the page files
4. Update spacing, typography, and shadows to match

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Troubleshooting

### API Connection Issues

If you see "Error connecting to API":

1. Verify backend is running: `http://localhost:8001/api/health`
2. Check `.env.local` has correct API URL
3. Ensure CORS is enabled in the backend

### Charts Not Displaying

1. Verify PNG files are in `public/assets/charts/`
2. Check file names match exactly (case-sensitive)
3. Clear Next.js cache: `rm -rf .next`

### Port Already in Use

If port 3000 is in use, run on a different port:

```bash
PORT=3001 npm run dev
```

## Production Deployment

For production deployment:

1. Build the application:
```bash
npm run build
```

2. Update `.env.local` with production API URL

3. Deploy using a platform like Vercel, Netlify, or your own server:
```bash
npm start
```

## License

MIT

## Support

For issues or questions, refer to the main project documentation.
