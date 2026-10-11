"""Email notifications (sent in a background thread so the website never waits on Gmail)."""
import smtplib
import threading
from email.message import EmailMessage

from . import config, database


def _send(msg):
    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as server:
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)


def notify_new_enquiry(enquiry_id, data):
    """Email the company about a new enquiry and (optionally) auto-reply to the customer."""
    if not config.SMTP_PASSWORD:
        print("SMTP_PASSWORD not set - skipping email (the enquiry is still saved).", flush=True)
        return

    service_label = config.SERVICES.get(data["service"], data["service"])

    def worker():
        try:
            note = EmailMessage()
            note["Subject"] = f"New Trivora enquiry #{enquiry_id}: {service_label}"
            note["From"] = f"Trivora Website <{config.SMTP_USER}>"
            note["To"] = config.NOTIFY_TO
            note["Reply-To"] = data["email"]
            note.set_content(
                "You have a new enquiry from the Trivora website.\n\n"
                f"Name:    {data['name']}\n"
                f"Email:   {data['email']}\n"
                f"Phone:   {data['phone'] or '-'}\n"
                f"Service: {service_label}\n"
                f"Budget:  {data['budget'] or '-'}\n\n"
                f"Message:\n{data['message']}\n\n"
                "See everything in your admin dashboard (/admin/).\n"
            )
            _send(note)

            if config.SEND_AUTOREPLY:
                reply = EmailMessage()
                reply["Subject"] = "We received your request - Trivora Technologies"
                reply["From"] = f"Trivora Technologies <{config.SMTP_USER}>"
                reply["To"] = data["email"]
                reply["Reply-To"] = config.COMPANY["email"]
                phones = ", ".join(p["display"] for p in config.COMPANY["phones"])
                reply.set_content(
                    f"Hi {data['name']},\n\n"
                    "Thank you for contacting Trivora Technologies. We have received your request "
                    "and a member of our team will get back to you shortly.\n\n"
                    "If it is urgent, call or WhatsApp us on:\n"
                    f"  {phones}\n\n"
                    f"Email: {config.COMPANY['email']}\n\n"
                    "Website development starts from KSh 30,000.\n\n"
                    "Regards,\nTrivora Technologies\n"
                )
                _send(reply)

            conn = database.connect()
            conn.execute("UPDATE enquiries SET notified = 1 WHERE id = ?", (enquiry_id,))
            conn.commit()
            conn.close()
        except Exception as exc:  # noqa: BLE001
            print("Email notification failed:", exc, flush=True)

    threading.Thread(target=worker, daemon=True).start()
