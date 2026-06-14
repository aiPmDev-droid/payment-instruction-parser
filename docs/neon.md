# Neon Database Setup

This project uses **Neon** for serverless PostgreSQL hosting. Neon is free-tier friendly and supports IPv4, making it compatible with Vercel.

## Setup

1. Go to [neon.tech](https://neon.tech) and sign up (GitHub login works).
2. Click **Create a project**.
3. Choose a name and region (e.g. **US East**).
4. Click **Create**.

## Get the Connection String

1. From the Neon dashboard, open your project.
2. Click **Connect** in the top right.
3. Under **Connection string**, select **URI** format.
4. Copy the string — it looks like:
```
postgresql://neondb_owner:password@ep-xxxxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

## Convert for the App

The app uses SQLAlchemy with the psycopg driver. Convert the URI:

| Original | Replaced With |
|----------|---------------|
| `postgresql://` | `postgresql+psycopg://` |
| Remove `&channel_binding=require` if present | (not supported by psycopg) |

Final format:
```
postgresql+psycopg://neondb_owner:password@ep-xxxxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

## Add to Vercel

1. Go to **Vercel Dashboard → Settings → Environment Variables**.
2. Add a variable named `DATABASE_URL` with the converted Neon URL.
3. Check the **Production** environment.
4. Save, then **Redeploy** your project.

## Verify

After redeploy, the health endpoint should work:
```
https://your-project.vercel.app/api/health
```
Upload a file and the extracted payments will be saved to Neon's PostgreSQL.