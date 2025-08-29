# services/auth_service/tools/send_test_code.py
import sys, secrets, smtplib
from email.message import EmailMessage

SMTP_HOST = "mailpit"
SMTP_PORT = 1025
MAIL_FROM = "no-reply@allures.local"
MAIL_FROM_NAME = "Allures"
EMAIL_CODE_TTL_MIN = 10

def gen_code(n=6) -> str:
    return f"{secrets.randbelow(10**n):0{n}d}"

def send_code(to_email: str, code: str):
    html = f"""
    <p>Вітаємо!</p>
    <p>Ваш код підтвердження:
       <strong style="font-size:20px">{code}</strong></p>
    <p>Код дійсний {EMAIL_CODE_TTL_MIN} хвилин.</p>
    """
    msg = EmailMessage()
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
    msg["To"] = to_email
    msg["Subject"] = "Підтвердження e-mail | Allures (тест)"
    msg.set_content(f"Verification code: {code}")  # plain text тоже с кодом
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:  # Mailpit: без TLS/логина
        s.send_message(msg)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_test_code.py <email>")
        sys.exit(1)
    email = sys.argv[1]
    code = gen_code(6)
    print("Sending code:", code, "to:", email)
    send_code(email, code)
    print("Done. Check http://localhost:8025")
