from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
from urllib.parse import quote
import requests  # For shortening URLs

app = Flask(__name__)
CORS(app)

EMAIL_ADDRESS = "fraudshieldpdp@gmail.com"
EMAIL_PASSWORD = "olxo hppx dnhn gknb"

def send_email(to_email, subject, message):
    msg = EmailMessage()
    msg.set_content(message, subtype="html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def shorten_url(long_url):
    try:
        response = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}")
        return response.text
    except:
        return long_url  

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        name = data["cardholder_name"]
        email = data["email"]
        amount = float(data["amount"])
        transaction_platform = data["transaction_platform"]

        base_url = "https://fraudshield.vercel.app"
        encoded_email = quote(email)
        encoded_amount = quote(str(amount))

        approve_link = shorten_url(f"{base_url}/approve?email={encoded_email}&amount={encoded_amount}")
        decline_link = shorten_url(f"{base_url}/decline?email={encoded_email}&amount={encoded_amount}")

        fraud_email_content = f"""
        🚨 <b>Fraud Alert!</b> 🚨<br>
        Dear {name},<br><br>

        Your transaction of <b>₹{amount}</b> for <b>{transaction_platform}</b> has been flagged as suspicious.<br>
        <b>Reason:</b> Transaction amount exceeds ₹3000.<br><br>

        ✅ <a href="{approve_link}" target="_blank">Approve Transaction</a><br>
        ❌ <a href="{decline_link}" target="_blank">Decline Transaction</a><br><br>

        Regards,<br>
        🏦 FraudShield Security Team
        """
        send_email(email, "⚠️ Fraud Alert! Approve or Reject", fraud_email_content)
        return jsonify({"message": "⚠️ Fraud Detected! Approval email sent."})

    except Exception as e:
        return jsonify({"error": f"Error processing request: {e}"}), 500

@app.route("/approve", methods=["GET"])
def approve_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    confirmation_email_content = f"Your transaction of ₹{amount} has been <b>approved</b>."
    send_email(email, "✅ Transaction Approved", confirmation_email_content)

    return redirect("https://fraudshield.vercel.app/approved")

@app.route("/decline", methods=["GET"])
def decline_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    confirmation_email_content = f"Your transaction of ₹{amount} has been <b>declined</b>."
    send_email(email, "❌ Transaction Declined", confirmation_email_content)

    return redirect("https://fraudshield.vercel.app/declined")

if __name__ == "__main__":
    app.run()