import json
import smtplib

import stock_data_fetching

from email.mime.text import MIMEText

# smtp_password = 'password123@'
APP_PASSWORD = "vlkt xwfq bdir trle"
SENDER = 'stock.price.notifier4@gmail.com'
# recipients = [SENDER, 'vdvasilev04@gmail.com']
# subject = 'Hello, world!'
# body = 'This is a test email.'


def send_email(subject: str, body: str, recipients: list) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(SENDER, APP_PASSWORD)
            smtp_server.sendmail(SENDER,
                                 recipients,
                                 msg.as_string())
            print("Message sent!")
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as e:
        print(f"Failed to send email: {e}")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")


def save_email(email: str) -> None:
    with open(stock_data_fetching.SAVED_STOCKS_FILE,
              "r",
              encoding="utf-8") as file:
        data = json.load(file)
    data["EMAIL"] = email

    with open(stock_data_fetching.SAVED_STOCKS_FILE,
              "w",
              encoding="utf-8") as file:
        json.dump(data, file)


def get_email() -> str:
    with open(stock_data_fetching.SAVED_STOCKS_FILE,
              "r",
              encoding="utf-8") as file:
        data = json.load(file)
    return data["EMAIL"]
