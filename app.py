from flask import Flask, render_template, request, redirect, flash, url_for
import re
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = "lumens_ndp_secret_key"

CREDS_FILE = "google-service-account.json"
SPREADSHEET_NAME = "Lumens Registration"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_worksheet():
    credentials = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(SPREADSHEET_NAME)
    return spreadsheet.sheet1


def ensure_headers():
    worksheet = get_worksheet()
    headers = worksheet.row_values(1)

    expected_headers = [
        "Timestamp",
        "Relationship Manager",
        "Title",
        "Name",
        "Gender",
        "Contact Number",
        "Car Plate Number"
    ]

    if not headers:
        worksheet.append_row(expected_headers)


def save_to_google_sheet(rm, title, name, gender, contact_number, carplate):
    ensure_headers()
    worksheet = get_worksheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    worksheet.append_row([
        timestamp,
        rm,
        title,
        name,
        gender,
        contact_number,
        carplate
    ])


@app.route("/", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        rm = request.form.get("rm", "").strip()
        gender = request.form.get("gender", "").strip()
        name = request.form.get("name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        carplate = request.form.get("carplate", "").strip().upper()

        if gender == "Male":
            title = "Mr"
        elif gender == "Female":
            title = "Ms"
        else:
            title = ""

        if not rm or not gender or not name or not contact_number or not carplate:
            flash("Please complete all fields before submitting.", "error")
            return redirect(url_for("registration") + "#registration-form")

        if not re.fullmatch(r"\d{8}", contact_number):
            flash("Contact number must be exactly 8 digits.", "error")
            return redirect(url_for("registration") + "#registration-form")

        try:
            save_to_google_sheet(rm, title, name, gender, contact_number, carplate)
            flash(
                f"Hi {name}, thank you for registering for the Lumens NDP Decal Campaign as we celebrate Singapore’s 61st year of independence.",
                "success"
            )
        except Exception as e:
            flash(f"Error: {str(e)}", "error")

        return redirect(url_for("registration") + "#registration-form")

    return render_template("registration.html")


if __name__ == "__main__":
    app.run(debug=True)