import requests

url = "http://192.168.39.147:5000/predict"  # Change this to your actual server IP
data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "amount": 5000,
    "platform": "E-commerce"
}

response = requests.post(url, json=data)

# Print API response
print("Response Status:", response.status_code)
print("Response JSON:", response.json())
