---
description: Run the Next.js frontend standalone (without Docker)
---

# Run Frontend Standalone

Start the Next.js 15 dev server directly for faster UI iteration.

## Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000` (via Docker or standalone)

## Steps

// turbo
1. Install dependencies:
```
npm install
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\frontend`

2. Start the Next.js dev server:
```
npm run dev
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\frontend`

The dev server runs at `http://localhost:3000` with hot-module replacement.

3. Open `http://localhost:3000` in the browser to verify.

## Environment

The frontend uses `NEXT_PUBLIC_API_URL` to connect to the backend. If not set, it defaults to the Docker internal URL. For standalone dev, create a `.env.local` in the frontend directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Build & Lint

- **Build for production**: `npm run build`
- **Run production server**: `npm run start`
- **Lint**: `npm run lint`
