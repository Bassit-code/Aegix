# 🛡️ Aegix – Secure Code Scanner
![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-BY--NC--ND%204.0-lightgrey.svg)


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


- `app.py`: Flask server logic
- `scanner.py`: Scanning engine and AI integration
- `templates/index.html`: Frontend interface
- `static/`: Icons, sounds, assets
- `uploads/`: Temp directory for scan input (auto-created)



---

## 📸 Screenshots

*(Screenshots coming soon)*

---

## 📄 Licence

This project is licensed under the [Creative Commons BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) licence.

You may view and share the code for personal or educational use, but **you may not reuse, modify, or redistribute it** without explicit permission.

© 2025 Bassit Irfan

---

**Author:** Bassit Irfan  
[LinkedIn](https://www.linkedin.com/in/bassit-irfan)  
[Portfolio](https://bassit-code.github.io)
