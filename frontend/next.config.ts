import type { NextConfig } from 'next'

// No /api rewrite: FastAPI is reached only from the Next.js server, via
// src/lib/backend.ts (ADR 0004).
const nextConfig: NextConfig = {}

export default nextConfig
