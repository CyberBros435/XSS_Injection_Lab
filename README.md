<div align="center">

```
 __  __ ____ ____    ___        _           _   _               
 \ \/ // ___/ ___|  |_ _|_ __  (_) ___  ___| |_(_) ___  _ __   
  \  / \___ \___ \   | || '_ \ | |/ _ \/ __| __| |/ _ \| '_ \  
  /  \  ___) |__) |  | || | | || |  __/ (__| |_| | (_) | | | | 
 /_/\_\|____/____/  |___|_| |_|/ |\___|\___|\__|_|\___/|_| |_| 
                              |__/                               
 __          __   _       __     ___   _ _                _     
 \ \        / /  | |      \ \   / / | | | |              | |    
  \ \  /\  / /_ _| |___    \ \_/ /| | | | |  __ _  ___  | |__  
   \ \/  \/ / _` | / __|    \   / | | | | | / _` |/ _ \ | '_ \ 
    \  /\  / (_| | \__ \     | |  | |_| | || (_| |  __/ | |_) |
     \/  \/ \__,_|_|___/     |_|   \___/|_| \__,_|\___| |_.__/ 
```

# 🧪 XSS Injection Lab — Hands-On Web Security Practice Lab

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Local%20Only-red?style=flat-square)]()
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen?style=flat-square)]()
[![Author](https://img.shields.io/badge/Author-Cyber%20Bro's-purple?style=flat-square)](https://github.com/CyberBros435)

> **A fully local, intentionally vulnerable web lab built for cybersecurity students.**  
> Practice Reflected XSS, Stored XSS, unsafe rendering, and comment injection — then flip to Safe Mode and see exactly how to fix each vulnerability. No external dependencies. Runs entirely on Python's standard library.

> ⚠️ **WARNING: Run locally only. Never expose this server to the internet.**

</div>

---

## 📌 Table of Contents

- [About](#-about)
- [What You Will Learn](#-what-you-will-learn)
- [Lab Modules](#-lab-modules)
- [How It Works](#-how-it-works)
- [Requirements](#-requirements)
- [Quick Start (One Command)](#-quick-start-one-command)
- [Step-by-Step Setup](#-step-by-step-setup)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Seeded Lab Data](#-seeded-lab-data)
- [Safe vs Vulnerable Mode](#-safe-vs-vulnerable-mode)
- [Related Projects](#-related-projects)
- [Author](#-author)
- [Disclaimer](#-disclaimer)

---

## 🧠 About

**XSS Injection Lab** is a deliberately vulnerable web application that runs entirely on your local machine. It simulates real-world web security vulnerabilities in a safe, controlled environment — so students can **attack**, **understand**, and **fix** each vulnerability without any risk.

The backend is a pure Python HTTP server (zero external dependencies). The frontend is plain HTML, CSS, and JavaScript. The database is SQLite — auto-created and seeded on first run. No Docker, no frameworks, no setup headaches.

---

## 🎓 What You Will Learn

Every module in this lab teaches a real-world web security concept that is tested in **CTFs, bug bounties, and penetration testing certifications** (CEH, OSCP, eWPT):

| # | Concept | What You Practice |
|---|---|---|
| 1 | **Reflected XSS** | Injecting scripts via URL query parameters |
| 2 | **Stored XSS** | Persisting malicious scripts in a database |
| 3 | **Unsafe HTML Rendering** | Seeing how `innerHTML` executes injected code |
| 4 | **Safe HTML Rendering** | Using `textContent` / escaping to neutralize payloads |
| 5 | **HTTP API Behavior** | Crafting GET and POST requests manually |
| 6 | **SQLite Database** | Understanding how user input reaches a database |
| 7 | **Comment Injection** | Submitting malicious comments via a form |
| 8 | **Security Headers** | Observing what headers are missing and why they matter |
| 9 | **Path Traversal Prevention** | How the server blocks `../` directory escapes |
| 10 | **Vulnerable vs Secure Code** | Comparing broken code side-by-side with the fix |

---

## 🔬 Lab Modules

### 🔴 Module 1 — Reflected XSS
**Endpoint:** `GET /api/reflected?q=<payload>`

The server reflects your input directly back in the JSON response without sanitization. The frontend renders this into the page using `innerHTML`.

**Try this payload:**
```
http://127.0.0.1:8000/api/reflected?q=<script>alert('XSS')</script>
```

**What you observe:** The script executes in the browser.  
**What you learn:** How unsanitized URL parameters lead to Reflected XSS.

---

### 🔴 Module 2 — Stored XSS (Comment Injection)
**Endpoint:** `POST /api/comments`

Submit a comment containing an HTML or JavaScript payload. The comment is stored in the SQLite database and rendered back to every user who loads the page.

**Try this payload via the comment form:**
```html
<img src=x onerror="alert('Stored XSS')">
```

**What you observe:** Every page load triggers the payload for all users.  
**What you learn:** Why stored/persistent XSS is more dangerous than reflected XSS.

---

### 🟡 Module 3 — Unsafe vs Safe Rendering
The lab UI includes a **toggle switch** between Vulnerable Mode and Safe Mode.

| Mode | Method Used | Result |
|---|---|---|
| 🔴 Vulnerable | `element.innerHTML = data` | HTML tags and scripts execute |
| 🟢 Safe | `element.textContent = data` | Everything rendered as plain text |

**What you learn:** A single line of JavaScript is the difference between a secure and an insecure application.

---

### 🟡 Module 4 — HTTP API Exploration
**Endpoints:** `/api/users`, `/api/comments`, `/api/health`

Explore the API directly in your browser or with `curl`. Observe how data flows from the database to the frontend with no authentication layer.

**Try:**
```bash
curl http://127.0.0.1:8000/api/users
curl http://127.0.0.1:8000/api/comments
```

**What you learn:** How unauthenticated API endpoints expose sensitive data, and why access control matters.

---

### 🟢 Module 5 — Path Traversal Prevention
The static file server validates every file path before serving it. Attempts to escape the app directory are blocked.

**What you learn:** How `path.resolve()` and prefix checks prevent directory traversal attacks (`../../../../etc/passwd`).

---

## ⚙️ How It Works

```
Browser (HTML/CSS/JS)
        │
        ▼
Python ThreadingHTTPServer  ←──── server.py
        │
        ├── GET  /api/reflected     ← Reflected XSS endpoint
        ├── GET  /api/comments      ← Fetch stored comments
        ├── POST /api/comments      ← Submit new comment (stored XSS target)
        ├── GET  /api/users         ← Fetch seeded users
        ├── GET  /api/health        ← Health check
        └── GET  /html /css /js     ← Static file serving
                │
                ▼
         SQLite Database
         data/lab.db
         ├── users table
         └── comments table
```

- **No Flask, no Django, no Node.js** — pure Python `http.server`
- **Database auto-created** on first run with seed data
- **Intentionally minimal security headers** — part of the learning experience
- **ThreadingHTTPServer** handles multiple requests simultaneously

---

## ⚙️ Requirements

- **OS:** Windows / Linux / macOS
- **Python:** 3.7 or higher
- **No external dependencies** — uses Python standard library only

> `sqlite3`, `http.server`, `json`, `pathlib`, `urllib.parse` are all built into Python.

---

## ⚡ Quick Start (One Command)

```bash
git clone https://github.com/CyberBros435/XSS_Injection_Lab.git && cd XSS_Injection_Lab && python server.py
```

Then open your browser and go to:

```
http://127.0.0.1:8000
```

---

## 🛠️ Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/CyberBros435/XSS_Injection_Lab.git
```

### 2. Navigate into the Project Directory

```bash
cd XSS_Injection_Lab
```

### 3. Run the Server

```bash
python server.py
```

You should see:

```
[Vulnerable Lab] Running on: http://127.0.0.1:8000
[DB] /path/to/XSS_Injection_Lab/data/lab.db
Press CTRL+C to stop.
```

### 4. Open in Browser

```
http://127.0.0.1:8000
```

### 5. Stop the Server

```
CTRL + C
```

> The SQLite database (`data/lab.db`) is created automatically on first run. No setup needed.

---

## 📁 Project Structure

```
XSS_Injection_Lab/
│
├── server.py                  # Python HTTP server + all API logic
│
├── html/
│   └── lab.html               # Main lab frontend (single page)
│
├── css/
│   └── style.css              # Lab UI styling
│
├── js/
│   └── app.js                 # Frontend logic (fetch, render, toggle)
│
├── data/                      # Auto-created on first run
│   └── lab.db                 # SQLite database (users + comments)
│
└── README.md                  # Project documentation
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Vulnerability |
|---|---|---|---|
| `GET` | `/api/reflected?q=` | Reflects query param in response | 🔴 Reflected XSS |
| `GET` | `/api/comments` | Returns all stored comments | 🔴 Stored XSS (if rendered unsafe) |
| `POST` | `/api/comments` | Stores a new comment | 🔴 Stored XSS input |
| `GET` | `/api/users` | Returns all seeded users | 🟡 No auth / data exposure |
| `GET` | `/api/health` | Server + DB health check | 🟢 Safe |
| `GET` | `/` | Serves `lab.html` | 🟢 Static |

### POST `/api/comments` — Request Body

```json
{
  "name": "YourName",
  "comment": "Your comment or payload here"
}
```

### Example with curl

```bash
# Reflected XSS test
curl "http://127.0.0.1:8000/api/reflected?q=<script>alert(1)</script>"

# Post a stored XSS payload
curl -X POST http://127.0.0.1:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"name":"Hacker","comment":"<img src=x onerror=alert(1)>"}'

# Fetch all comments
curl http://127.0.0.1:8000/api/comments

# Fetch all users
curl http://127.0.0.1:8000/api/users
```

---

## 🌱 Seeded Lab Data

The database is pre-populated on first run so the lab is ready to use immediately:

### Users Table

| ID | Username | Email | Bio |
|---|---|---|---|
| 1 | alice | alice@example.com | Hi, I'm Alice. I love web security labs. |
| 2 | bob | bob@example.com | Bob here. Practicing XSS and safe coding. |
| 3 | charlie | charlie@example.com | Charlie: learning secure frontend patterns. |

### Comments Table (Pre-seeded)

| Name | Comment |
|---|---|
| Admin | Welcome to the lab! Try the modules on the left. |
| Alice | This is a `<b>bold</b>` comment (HTML inside). |
| Bob | Try switching between Vulnerable vs Safe render modes. |

---

## 🔄 Safe vs Vulnerable Mode

The lab UI includes a **mode toggle** that demonstrates the fix for every rendering vulnerability:

```
🔴 VULNERABLE MODE          🟢 SAFE MODE
─────────────────           ────────────────────
innerHTML = data     →      textContent = data
Scripts execute      →      Everything is plain text
HTML tags render     →      Tags shown as literal text
XSS works            →      XSS neutralized
```

**This is the most important lesson in the lab:** the difference between a vulnerable and a secure application is often just one property — `innerHTML` vs `textContent`.

---

## 🔗 Related Projects

> Part of the **CyberBros435** network & security toolkit collection:

| Tool | Description | Link |
|---|---|---|
| 🔍 **IP Scanner** | IPv4 scanner, ping, tracert & ipconfig | [CyberBros435/IP_Scanner](https://github.com/CyberBros435/IP_Scanner) |
| 🌐 **DNS Server** | Hostname to IPv4 resolver | [CyberBros435/DNS_Server](https://github.com/CyberBros435/DNS_Server) |
| #️⃣ **Hash Generator** | Text to hash converter | [CyberBros435/Hash_Generator](https://github.com/CyberBros435/Hash_Generator) |
| 🔎 **Hash Identifier** | Identify unknown hash types | [CyberBros435/Hash_Identifier](https://github.com/CyberBros435/Hash_Identifier) |
| 🔐 **Hash Cracker** | Dictionary-based hash cracker | [CyberBros435/Hash_Cracker](https://github.com/CyberBros435/Hash_Cracker) |
| 🧪 **XSS Injection Lab** | Hands-on web security practice lab *(this repo)* | [CyberBros435/XSS_Injection_Lab](https://github.com/CyberBros435/XSS_Injection_Lab) |

---

## 👤 Author

**Cyber Bro's**  
🔗 GitHub: [@CyberBros435](https://github.com/CyberBros435)  
📦 Repository: [CyberBros435/XSS_Injection_Lab](https://github.com/CyberBros435/XSS_Injection_Lab)

---

## ⚠️ Disclaimer

> This lab is **intentionally vulnerable by design** and is intended **for educational purposes only.**  
> **Run it locally only.** Never deploy this server on a public IP, VPS, or any network-accessible machine.  
> The author is **not responsible** for any misuse of this software.  
> Always practice ethical hacking **only on systems you own or have explicit permission to test.**

---

<div align="center">

Made with ❤️ by [Cyber Bro's](https://github.com/CyberBros435) · ⭐ Star this repo if you found it useful!

</div>
