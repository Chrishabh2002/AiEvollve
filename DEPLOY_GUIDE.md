# 🚀 Ultimate Deployment Guide: Vercel + Render

You asked for the best setup. Here is the **Industry Standard** for this tech stack (Next.js + Python):

## 🏛️ The Architecture
We will split the app into two parts for maximum performance:
1.  **Frontend (UI)** -> **Vercel** (Best for Next.js, super fast CDN).
2.  **Backend (The Brain)** -> **Render** (Best for Python/Docker, allows persistent disks).

---

## Part 1: Deploy Backend (Render)
1.  Push your code to GitHub.
2.  Go to **[dashboard.render.com](https://dashboard.render.com)**.
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repo `AiEvollve`.
5.  **Configuration**:
    -   **Name**: `aievollve-brain`
    -   **Runtime**: `Python 3`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
6.  **Environment Variables**:
    -   Add `PYTHON_VERSION` = `3.11.0`
7.  **Disks (Crucial!)**:
    -   Scroll down to "Disks".
    -   Add a disk named `world_data`.
    -   Mount path: `/app/data`
    -   Size: 1GB.
    -   *Why? This saves your agents' memories so they don't reset.*
8.  Click **Create Web Service**.
9.  **Copy the URL** (e.g., `https://aievollve-brain.onrender.com`). You need this for Part 2.

---

## Part 2: Deploy Frontend (Vercel)
1.  Go to **[vercel.com](https://vercel.com)**.
2.  "Add New..." -> "Project".
3.  Import `AiEvollve`.
4.  **Framework Preset**: It should auto-detect `Next.js`.
5.  **Root Directory**: Click "Edit" and select `frontend`.
6.  **Environment Variables**:
    -   Key: `NEXT_PUBLIC_API_BASE`
    -   Value: `https://aievollve-brain.onrender.com` (The URL from Part 1).
7.  Click **Deploy**.

---

## ❓ Comparison: Why not others?

| Platform | Best For | Verdict |
| :--- | :--- | :--- |
| **Vercel** | Frontend / Next.js | **🏆 WINNER for UI** |
| **Render** | Backend / Python | **🏆 WINNER for Backend** (Supports Disks) |
| **Netlify** | Frontend (Alternative) | Good, but Vercel is made by Next.js creators. |
| **Railway** | Full Stack (All-in-one) | Great alternative if you want everything in one place. |

### ✅ Deployment Checklist
- [x] Code Pushed to GitHub
- [x] Backend deployed on Render (wait for "Live" status)
- [x] Backend URL copied
- [x] Frontend deployed on Vercel with `NEXT_PUBLIC_API_BASE` set
