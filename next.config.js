/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const upstream = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/market-api/:path*",
        destination: `${upstream}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
