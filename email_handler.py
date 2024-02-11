"""
Module for handling email notifications, including:
- Sending emails via SMTP
- Storing and retrieving email addresses.
"""
import json
import smtplib

from email.mime.text import MIMEText

import stock_data_fetching

# smtp_password = 'password123@'
APP_PASSWORD = "vlkt xwfq bdir trle"
SENDER = 'stock.price.notifier4@gmail.com'


def send_email(subject: str, body: str, recipients: list) -> None:
    """
    Send an email with the provided subject, body, and recipients.

    Parameters:
        subject (str): The subject of the email.
        body (str): The body of the email.
        recipients (list): A list of email addresses to send the email to.

    Returns:
        None
    """
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
    """
    Save the provided email address to a JSON file.

    Parameters:
        email (str): The email address to save.

    Returns:
        None
    """
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
    """
    Retrieve the saved email address from the JSON file.

    Returns:
        str: The retrieved email address.
    """
    with open(stock_data_fetching.SAVED_STOCKS_FILE,
              "r",
              encoding="utf-8") as file:
        data = json.load(file)
    return data["EMAIL"]
