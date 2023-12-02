import requests
import selectorlib
import smtplib
import ssl
import os
import sqlite3
import time

URL = 'http://programmer100.pythonanywhere.com/tours/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect('Data.db')


def scrape(url):
    """ Scrape the page source from the URL """
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def store(extracted_l):
    row_s = extracted_l.split(",")
    row_s = [item.strip() for item in row_s]
    cursor_s = connection.cursor()
    cursor_s.execute("INSERT INTO events VALUES (?,?,?)", row_s)
    connection.commit()


def read(extracted_r):
    row = extracted_r.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


def send_email(message):
    host = 'smtp.gmail.com'
    port = 465

    username = 'huberwrat@gmail.com'
    password = os.getenv("PASSWORD")

    receiver = 'regidancodes@gmail.com'
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent")


info = "Hey! a new content was found at Tours.com"
raw_messages = f"""\
Subject: Web scraping email
{info}
"""

if __name__ == '__main__':
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)

        if extracted != "No upcoming tours":
            row_g = read(extracted)
            if not row_g:
                store(extracted)
                send_email(message=raw_messages)
        time.sleep(5)
