/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const upstream = process.env.API_INTERNAL_URL || "http://nordvex-api.railway.internal:8080";
    return [
      {
        source: "/market-api/:path*",
        destination: `${upstream}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
