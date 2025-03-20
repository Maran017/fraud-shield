from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__, template_folder="../templates")  # Ensure templates are correctly referenced

# ✅ Allow CORS for frontend hosted on Vercel
CORS(app)

# ✅ Homepage route (Now serves index.html)
@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'index.html' is inside 'templates' folder

# ✅ Transaction history storage
transaction_history = {}

# ✅ Email Credentials (Move to environment variables in production)
EMAIL_ADDRESS = "fraudshieldpdp@gmail.com"
EMAIL_PASSWORD = "olxo hppx dnhn gknb"

# ✅ Function to send email alerts
def send_email(to_email, subject, message):
    msg = EmailMessage()
    msg.set_content(message)
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

# ✅ Fraud detection logic
def detect_fraud(email, amount):
    is_fraud = False
    reason = ""

    if amount > 3000:
        is_fraud = True
        reason = "Transaction amount exceeds ₹3000."

    if email in transaction_history:
        transaction_history[email].append(amount)
        if len(transaction_history[email]) >= 3:
            is_fraud = True
            reason = "Multiple rapid transactions detected."
    else:
        transaction_history[email] = [amount]

    return is_fraud, reason

# ✅ API Endpoint for Fraud Detection
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        name = data["cardholder_name"]
        email = data["email"]
        amount = float(data["amount"])
        card_number = data["card_number"]
        transaction_platform = data["transaction_platform"]

        is_fraud, reason = detect_fraud(email, amount)

        if is_fraud:
            base_url = "https://fraudshield.vercel.app"
            approve_link = f"{base_url}/approve?email={email}&amount={amount}"
            decline_link = f"{base_url}/decline?email={email}&amount={amount}"

            fraud_email_content = f"""
            🚨 **Fraud Alert!** 🚨
            Dear {name},

            Your transaction of **₹{amount}** for **{transaction_platform}** has been flagged as suspicious.  
            **Reason:** {reason}  

            ✅ [Approve Transaction]({approve_link})  
            ❌ [Decline Transaction]({decline_link})  

            Regards,  
            🏦 FraudShield Security Team
            """
            send_email(email, "⚠️ Fraud Alert! Approve or Reject", fraud_email_content)
            return jsonify({"message": "⚠️ Fraud Detected! Approval email sent.", "reason": reason})

        else:
            normal_email_content = f"""
            ✅ **Transaction Successful** ✅
            Dear {name},

            Your card ending in **{card_number[-4:]}** has been used for a purchase at **{transaction_platform}**.  
            The amount of **₹{amount}** has been successfully spent.

            Regards,  
            🏦 FraudShield Security Team
            """
            send_email(email, "✅ Transaction Approved", normal_email_content)
            return jsonify({"message": "✅ Transaction Approved."})

    except Exception as e:
        return jsonify({"error": f"Error processing request: {e}"}), 500

# ✅ Approve and Decline Routes
@app.route("/approve", methods=["GET"])
def approve_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    confirmation_email_content = f"Your transaction of ₹{amount} has been **approved**."
    send_email(email, "Transaction Approved", confirmation_email_content)
    
    return redirect("https://fraudshield.vercel.app/approved")

@app.route("/decline", methods=["GET"])
def decline_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    confirmation_email_content = f"Your transaction of ₹{amount} has been **declined**."
    send_email(email, "Transaction Declined", confirmation_email_content)
    
    return redirect("https://fraudshield.vercel.app/declined")

# ✅ Flask App Entry Point
if __name__ == "__main__":
    app.run()
