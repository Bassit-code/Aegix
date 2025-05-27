# 🛡️ Aegix – Secure Code Scanner

**Aegix** is a web-based tool that scans source code to detect common security vulnerabilities, including:

- 📝 Sensitive comments (e.g., TODOs, leaked information in comments)
- 🔑 Hardcoded secrets (e.g., passwords, API keys)
- ⚠️ Insecure error messages (e.g., `print(e)`, raw tracebacks)

> *Aegix was developed as part of my Final Year Project for the BSc Computer Science degree at Aston University.*

---

## 🚀 Features

- Upload a single file or a ZIP directory of code
- Supports multiple file types: `.py`, `.js`, `.java`, `.html`, `.php`, `.c`, `.cpp`, `.sh`, `.yaml`, `.json`
- Generates downloadable reports in **CSV**, **HTML**, **JSON**, or **PDF**
- Provides **AI-powered security recommendations** using OpenRouter
- Clean, responsive UI with dark mode and scanning animation

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Scanning Logic:** Regex-based vulnerability detection
- **AI Integration:** OpenRouter API for contextual advice
- **Reporting:** CSV, JSON, HTML, PDF (via `reportlab`)
- **Environment Management:** `python-dotenv`

---

## 🔐 API Key Required

Aegix requires an [OpenRouter](https://openrouter.ai) API key to generate AI-based security recommendations.  
For security reasons, the `.env` file containing the key is not included in this public repository.

---

## 📂 Project Structure

Aegix/
│
├── app.py # Flask server logic
├── scanner.py # Vulnerability scanning and AI integration
├── templates/
│ └── index.html # Web interface
├── static/ # Assets (icons, sounds, etc.)
└── uploads/ # Temporary upload directory (auto-created)


---

## 📸 Screenshots

*(Screenshots coming soon — or include some from the live demo interface and report output)*

---

## 📄 Licence

This project was developed for academic and portfolio use.  
© 2025 Bassit Irfan. This project is not licensed for reuse or modification without explicit permission.

---

**Author:** Bassit Irfan  
[LinkedIn](https://www.linkedin.com/in/bassit-irfan)  
[Portfolio](https://bassit-code.github.io)
