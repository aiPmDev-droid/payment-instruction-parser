/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    if (process.env.VERCEL) {
      // On Vercel: route to the Python serverless function
      return [
        {
          source: "/api/:path*",
          destination: "/api/index.py",
        },
      ];
    }
    // Locally: proxy to FastAPI running on :8000
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
