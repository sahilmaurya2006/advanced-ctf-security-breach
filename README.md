# 🔐 Advanced CTF: Security System Breach

**Difficulty**: Advanced | **Time Target**: ~1 hour | **Flag Count**: 1

## Challenge Overview

You've been tasked with breaking into a sophisticated security system. The system has multiple layers of protection:

1. **Web Application Layer** - Find hidden endpoints and exploit vulnerabilities
2. **Authentication Layer** - Decrypt credentials and bypass security
3. **Data Layer** - Extract secrets from encoded/encrypted data
4. **Final Layer** - Combine all clues to retrieve the flag

The flag format is: `CTF{...}`

---

## Getting Started

### Prerequisites
- Python 3.8+
- Docker (optional, for containerized setup)
- Basic understanding of: cryptography, web exploitation, reverse engineering

### Setup

**Option 1: Direct Python**
```bash
cd web_server
pip install -r requirements.txt
python app.py
```

**Option 2: Docker**
```bash
docker build -t ctf-challenge .
docker run -p 5000:5000 ctf-challenge
```

Server will run on `http://localhost:5000`

---

## Hints (Spoiler Warning! ⚠️)

### Hint Level 1: Discovery
- Look at the source code and configuration files
- Check for hardcoded values and comments
- Inspect HTTP headers and responses carefully

### Hint Level 2: Exploitation
- SQL injection vulnerabilities exist
- JWT tokens can be forged
- Base64 encoding is reversible

### Hint Level 3: Decryption
- You'll need a key (find it in the system)
- AES-256 encryption is used in one layer
- Combine information from multiple sources

### Hint Level 4: Final Flag
- The flag requires multi-stage decryption
- You need credentials, encryption keys, and hidden data
- Everything connects together

---

## Endpoints to Explore

- `GET /` - Main page
- `GET /login` - Login page
- `POST /login` - Login endpoint (vulnerable)
- `GET /admin` - Admin panel (restricted)
- `GET /api/config` - API endpoint
- `GET /api/status` - System status
- Hidden endpoints? Try common paths...

---

## Writeup

**For players:** If you're stuck, check `WRITEUP.md` in the repo after solving!

**For organizers:** Full solution available in `WRITEUP.md`

---

## Flag Submission

Submit your flag by running:
```bash
python verify_flag.py "CTF{your_flag_here}"
```

Or access the verification endpoint:
```bash
curl http://localhost:5000/api/verify?flag=CTF{your_flag_here}
```

---

## Challenge Structure

```
.
├── web_server/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Dependencies
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   └── admin.html
│   └── static/
│       ├── config.enc      # Encrypted configuration
│       └── data.txt        # Hidden data
├── Dockerfile
├── verify_flag.py          # Flag verification script
├── WRITEUP.md              # Complete solution
└── README.md               # This file
```

---

## Technical Details

- **Language**: Python (Flask)
- **Encryption**: AES-256-CBC
- **Authentication**: JWT with weak secret (intentional!)
- **Database**: SQLite with injection vulnerabilities
- **Encoding**: Base64, Hex, and custom algorithms

---

## Author Notes

This CTF is designed to test:
- Web application vulnerability assessment
- Cryptographic analysis
- Reverse engineering skills
- Information gathering and correlation
- Creative problem-solving

Good luck! 🎯

---

*Created for advanced CTF players. No professional security systems were harmed in the making of this challenge.*
