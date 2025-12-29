# Frontend Setup

## Quick Start

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Notes

- The frontend is configured to proxy API requests to `http://localhost:8000`
- Make sure the backend is running before using the frontend
- The app uses localStorage to persist user ID

