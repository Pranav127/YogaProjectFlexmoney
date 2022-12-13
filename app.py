from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
import datetime
import datetime
from apscheduler.schedulers.background import BackgroundScheduler



# Create a new Flask app
app = Flask(__name__)

# Set the location of the SQLite database
DB_FILE = "database.db"

@app.route("/")
def home():
    # Render the form template
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    # Get the form data from the request
    name = request.form.get("name")
    age = request.form.get("age")
    batch = request.form.get("batch")

    # Make sure the user is within the age limit
    if int(age) < 18 or int(age) > 65:
        # If not, redirect to the not eligible page
        return redirect(url_for("not_eligible"))

    # Otherwise, insert the form data into the database
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (name, age, batch) VALUES (?, ?, ?)", (name, age, batch))
        conn.commit()

    # Redirect to the payment page
    return redirect(url_for("payment"))

@app.route("/payment")
def payment():
    # This is where you would handle the payment processing
    # and display a payment page to the user
    return render_template("payment.html")

@app.route("/not-eligible")
def not_eligible():
    # Render the not eligible template
    return render_template("not_eligible.html")

@app.route("/validate", methods=["POST"])
def validate():
    # Get the credit card number from the form data
    card_name = request.form.get("card_name")
    credit_card_number = request.form.get("credit_card_number")

    # Remove any non-digit characters from the credit card number
    credit_card_number = re.sub(r"\D", "", credit_card_number)

    # Check if the credit card number is valid using Luhn's algorithm
    is_valid = validate_credit_card_number(credit_card_number)

    # If the credit card number is valid, redirect to the thank you page
    if is_valid:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO payments (card_name) VALUES (?)", (card_name,))

            conn.commit()
        
        return render_template("thank_you.html")

    # Otherwise, redirect to the payment page with an error message
    return redirect(url_for("fail"))



def validate_credit_card_number(number):
    # Make sure the number contains at least one digit
    if not any(char.isdigit() for char in number):
        return False

    # Implement the rest of Luhn's algorithm here
    doubled_digits = []
    for i, digit in enumerate(reversed(number)):
        if i % 2 == 1:
            doubled_digits.append(int(digit) * 2)
        else:
            doubled_digits.append(int(digit))

    for i, doubled_digit in enumerate(doubled_digits):
        if doubled_digit >= 10:
            doubled_digits[i] = sum(map(int, str(doubled_digit)))

    total = sum(doubled_digits)

    return total % 10 == 0


@app.route("/thank_you", methods=["GET"])
def thank_you():
    # Get the credit card number from the form data
    credit_card_number = request.form.get("credit_card_number")

    # Make sure the credit card number is not None
    if credit_card_number:
        # Remove any non-digit characters from the credit card number
        credit_card_number = re.sub(r"\D", "", credit_card_number)

        # Check if the credit card number is valid using Luhn's algorithm
        card_is_valid = validate_credit_card_number(credit_card_number)

        # Check if the card is valid
        if card_is_valid:
            # If the card is valid, render the thank you template
            return render_template("thank_you.html")
        else:
            # If the card is not valid, redirect to the payment page with an error message
             return redirect(url_for("fail"))
    else:
        # If the credit card number is None, redirect to the payment page with an error message
        return redirect(url_for("payment", error="Please enter a credit card number"))


@app.route("/fail")
def fail():
    # Render the fail template
    return render_template("fail.html")



# Create a new Scheduler object
scheduler = BackgroundScheduler()

# Start the scheduler
scheduler.start()

def delete_user():
    # Query the database to find users who have not paid the fee
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM payments WHERE payment_date IS NULL")
        unpaid_users = c.fetchall()

    # Loop through the unpaid users and delete them from the database
    for user in unpaid_users:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM payments WHERE user_id = ?", (user[0],))
            conn.commit()



def schedule_delete_user():
    # Get the current time
    now = datetime.datetime.now()

    # Schedule the delete_user function to be called in one month
    run_at = now + datetime.timedelta(days=30)

    # Use the built-in Python scheduler to run the delete_user function
    # at the specified time
    scheduler.scheduler.add_job(delete_user, "date", run_date=run_at)











if __name__ == "__main__":
    # Run the app
    app.run(host='0.0.0.0', port=5000)


