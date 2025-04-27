// File: next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove swcMinify
  reactStrictMode: true,
  experimental: {
    // Enable turbopack
    turbopackMinify: true,
  }
};

export default nextConfig;