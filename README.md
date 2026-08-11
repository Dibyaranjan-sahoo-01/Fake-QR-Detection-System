# QRSentry — Fake QR Code Detection System

A full-stack cybersecurity web app that scans QR codes (image upload or live
webcam), decodes their content, analyzes any embedded URL for phishing or
malicious signals, and returns a 0–100 risk score with a **Safe / Suspicious
/ Dangerous** verdict.

Built with **Python, Flask, OpenCV, pyzbar, and SQLite**.

---

## Features

- 📤 Upload a QR code image (PNG/JPG/JPEG/BMP/GIF/WEBP)
- 📷 Live webcam QR scanning (capture a frame, decode server-side)
- 🔍 QR decoding via OpenCV preprocessing + pyzbar
- 🧠 Automatic URL vs. plain-text classification
- 🛡️ Phishing heuristics: HTTPS check, URL shorteners, raw IP hosts,
  suspicious keywords, long/obfuscated URLs, risky TLDs, subdomain count
- 🌐 Optional Google Safe Browsing / VirusTotal integration (via API keys)
- 📊 0–100 weighted risk score → Safe / Suspicious / Dangerous
- 🗂️ Persistent scan history (SQLite) with search & filters
- 📈 Dashboard with totals, breakdown, and a risk-distribution chart
- 📄 CSV export of scan history
- 🛠️ Admin panel (session-based login) to review and delete scans
- 🌑 Responsive, dark, terminal-inspired security UI

---

## Tech Stack

| Layer     | Tools |
|-----------|-------|
| Frontend  | HTML5, CSS3, Bootstrap 5, vanilla JavaScript, Chart.js |
| Backend   | Python 3, Flask, Flask-SQLAlchemy |
| QR / CV   | OpenCV (`opencv-python-headless`), `pyzbar` |
| Analysis  | `requests`, `validators`, `tldextract` |
| Database  | SQLite |

---

## Project Structure

```
FakeQRDetectionSystem/
├── app.py                  # App factory + entry point
├── config.py                # Environment configuration
├── requirements.txt
├── database/
│   ├── database.db          # Created automatically on first run
│   └── init_db.py           # Standalone DB init script
├── models/
│   └── scan_model.py         # ScanHistory SQLAlchemy model
├── routes/
│   ├── main_routes.py        # HTML page routes
│   ├── api_routes.py         # REST JSON API
│   └── admin_routes.py       # Admin panel + auth
├── services/
│   ├── qr_scanner.py          # OpenCV + pyzbar decoding
│   ├── url_analyzer.py        # URL structure parsing
│   ├── phishing_detector.py   # Heuristic + optional API checks
│   ├── risk_calculator.py     # Score → verdict mapping
│   ├── report_generator.py    # Dashboard aggregation
│   └── export_csv.py          # CSV report writer
├── utils/
│   ├── validators.py
│   ├── helpers.py
│   └── constants.py
├── static/
│   ├── css/ (style.css, dashboard.css, scanner.css)
│   ├── js/  (main.js, dashboard.js, scanner.js)
│   ├── images/
│   └── uploads/               # Uploaded QR images land here
├── templates/                 # Jinja2 templates
├── reports/csv/                # Generated CSV exports
└── sample_qr/                  # Sample QR images for testing
```

---

## Installation

### 1. Clone / unzip the project and enter the folder

```bash
cd FakeQRDetectionSystem
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note on pyzbar:** on Linux you may need the system `zbar` library:
> `sudo apt-get install libzbar0` (Debian/Ubuntu) or `brew install zbar` (macOS).

### 4. Initialize the database (optional — it auto-creates on first run)

```bash
python database/init_db.py
```

### 5. Run the app

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## Configuration

Environment variables (all optional, sensible defaults provided):

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | dev key (change in production) |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `DATABASE_URL` | Override the SQLite path | `sqlite:///database/database.db` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin panel credentials | `admin` / `admin123` |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Enables live Safe Browsing lookups | unset (disabled) |
| `VIRUSTOTAL_API_KEY` | Enables live VirusTotal lookups | unset (disabled) |

⚠️ **Change the default admin password and secret key before deploying anywhere public.**

---

## Risk Scoring

Each detected issue adds weighted points (capped at 100):

| Check | Points |
|---|---|
| No HTTPS | 15 |
| URL shortener | 20 |
| Raw IP address host | 25 |
| Suspicious keyword(s) | up to 30 |
| Long URL (>90 chars) | 10 |
| Obfuscation indicators | 20 |
| Invalid URL format | 15 |
| Suspicious TLD | 15 |
| Many subdomains (3+) | 10 |
| Flagged by Safe Browsing / VirusTotal | 40 each |

**Verdict thresholds:** `0–25` Safe · `26–55` Suspicious · `56–100` Dangerous
(tune in `config.py`).

---

## Sample QR Codes

The `sample_qr/` folder includes ready-to-test images:

- `safe_qr.png` — a clean HTTPS link (Safe)
- `phishing_qr.png` — HTTP + credential-harvesting keywords + risky TLD (Dangerous)
- `shortened_url_qr.png` — a bit.ly-style shortened link (Suspicious)
- `text_qr.png` — plain text content, no URL analysis performed (Safe)

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/scan/upload` | Upload an image (`qr_image` field) |
| POST | `/api/scan/webcam` | JSON `{"image": "data:image/png;base64,..."}` |
| GET | `/api/history?q=&result=&qr_type=` | Search/filter scan history |
| GET | `/api/history/<id>` | Fetch one scan |
| DELETE | `/api/history/<id>` | Delete one scan |
| GET | `/api/export/csv` | Download full history as CSV |
| GET | `/api/stats` | Dashboard statistics JSON |

---

## Security Notes

- This is a **heuristic** detector, not a guarantee — always exercise
  caution with unfamiliar QR codes regardless of the score shown.
- The bundled admin auth is intentionally minimal (plaintext-config
  credentials, session cookie). Replace with proper hashed credentials
  and a real user store before any production deployment.
- Uploaded files are renamed to random UUIDs and validated by extension;
  add virus scanning if accepting untrusted uploads at scale.

---

## License

Provided as-is for educational and portfolio use.
