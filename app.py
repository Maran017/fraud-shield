from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS  # Importing CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# ✅ Allow CORS requests from your frontend (http://127.0.0.1:5500)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})  

# ✅ Homepage route (Now serves index.html)
@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'index.html' is inside the 'templates' folder

# Store transaction history for fraud detection
transaction_history = {}

# ✅ Email Credentials (Updated)
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

    # Condition 1: Amount greater than ₹3000
    if amount > 3000:
        is_fraud = True
        reason = "Transaction amount exceeds ₹3000."

    # Condition 2: Rapid multiple transactions
    if email in transaction_history:
        transaction_history[email].append(amount)
        if len(transaction_history[email]) >= 3:  # 3 rapid transactions
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
        name = data["cardholder_name"]  # Correct key matching frontend
        email = data["email"]
        amount = float(data["amount"])
        card_number = data["card_number"]
        transaction_platform = data["transaction_platform"]

        # Detect fraud
        is_fraud, reason = detect_fraud(email, amount)

        if is_fraud:
            # Fraud alert email with approval and decline links
            base_url = "http://127.0.0.1:5000"  # Change to your hosted domain if deployed
            approve_link = f"{base_url}/approve?email={email}&amount={amount}"
            decline_link = f"{base_url}/decline?email={email}&amount={amount}"

            fraud_email_content = f"""
            🚨 **Fraud Alert!** 🚨
            Dear {name},

            Your transaction of **₹{amount}** for **{transaction_platform}** has been flagged as suspicious.  
            **Reason:** {reason}  

            Please approve or reject this transaction immediately.

            ✅ [Approve Transaction]({approve_link})  
            ❌ [Decline Transaction]({decline_link})  

            Your card ending in **{card_number[-4:]}** was used for this transaction.

            Regards,  
            🏦 FraudShield Security Team
            """
            send_email(email, "⚠️ Fraud Alert! Approve or Reject", fraud_email_content)
            return jsonify({"message": "⚠️ Fraud Detected! Approval email sent.", "reason": reason})

        else:
            # Normal transaction email content
            normal_email_content = f"""
            ✅ **Transaction Successful** ✅
            Dear {name},

            Your card ending in **{card_number[-4:]}** has been used for a purchase at **{transaction_platform}**.  
            The amount of **₹{amount}** has been successfully spent.

            Thank you for using FraudShield. If this was not you, please contact your bank immediately.

            Regards,  
            🏦 FraudShield Security Team
            """
            send_email(email, "✅ Transaction Approved", normal_email_content)
            return jsonify({"message": "✅ Transaction Approved."})

    except Exception as e:
        return jsonify({"error": f"Error processing request: {e}"}), 500

# ✅ Routes for Approve and Decline Actions
@app.route("/approve", methods=["GET"])
def approve_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    # Update transaction status to approved (In real life, store in DB)
    print(f"✅ Transaction approved for {email}, amount: ₹{amount}")
    
    # Send confirmation email to the user
    confirmation_email_content = f"""
    Your transaction of ₹{amount} has been **approved**.

    If you did not initiate this action, please contact your bank immediately.

    Regards,  
    🏦 FraudShield Security Team
    """
    send_email(email, "Transaction Approved", confirmation_email_content)
    
    return redirect("https://your-webpage.com/approved")  # Redirect to a page confirming the approval (e.g., confirmation page)

@app.route("/decline", methods=["GET"])
def decline_transaction():
    email = request.args.get('email')
    amount = float(request.args.get('amount'))

    # Update transaction status to declined (In real life, store in DB)
    print(f"❌ Transaction declined for {email}, amount: ₹{amount}")
    
    # Send confirmation email to the user
    confirmation_email_content = f"""
    Your transaction of ₹{amount} has been **declined**.

    If you did not initiate this action, please contact your bank immediately.

    Regards,  
    🏦 FraudShield Security Team
    """
    send_email(email, "Transaction Declined", confirmation_email_content)
    
    return redirect("https://your-webpage.com/declined")  # Redirect to a page confirming the decline (e.g., confirmation page)

# ✅ Run the Flask App
if __name__ == "__main__":
    print("✅ Fraud detection model running...")
    app.run(debug=True, host="0.0.0.0", port=5000)
