from flask import Flask, request, jsonify
import base64
from Crypto.Cipher import AES
import json
import os
from functools import wraps

app = Flask(__name__)

# Constants
BASE64_KEY = "X25ldHN5bmFfbmV0bW9kXw=="
KEY = base64.b64decode(BASE64_KEY)
Ezxx = "This Script Generated By : EstebanZxx\nBeta Test Module : V1\n=====================================\nResult Decrypt : \n"

# Decrypt function using AES ECB mode (maintained for backward compatibility)
def decrypt_aes_ecb_128(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.rstrip(b"\x00")  # Remove trailing null bytes

# Function to format decrypted content
def format_decrypted_content(decrypted_text):
    try:
        # Attempt to parse the decrypted text as JSON
        data = json.loads(decrypted_text)

        # Initialize an empty string to store the formatted text
        formatted_text = ""

        # Iterate through the key-value pairs in the JSON data
        for key, value in data.items():
            # Check if the value is a dictionary
            if isinstance(value, dict):
                # If it's a dictionary, iterate through its key-value pairs
                for sub_key, sub_value in value.items():
                    # Add the sub_key and sub_value to the formatted text with a newline
                    formatted_text += f"{sub_key} {sub_value}\n"
            # Check if the value is a list
            elif isinstance(value, list):
                # If it's a list, iterate through its items
                for item in value:
                    # Check if the item is a dictionary
                    if isinstance(item, dict):
                        # If it's a dictionary, iterate through its key-value pairs
                        for sub_key, sub_value in item.items():
                            # Add the sub_key and sub_value to the formatted text with a newline
                            formatted_text += f"{sub_key} {sub_value}\n"
                    # If the item is not a dictionary, add the key and item to the formatted text with a newline
                    else:
                        formatted_text += f"{key} {item}\n"
            # If the value is not a dictionary or a list, add the key and value to the formatted text with a newline
            else:
                formatted_text += f"{key} {value}\n"

        # Return the formatted text
        return formatted_text

    except json.JSONDecodeError:
        # If the decrypted text is not valid JSON, return the original decrypted text as a string
        return decrypted_text.decode('utf-8', errors='replace')

# Add a simple rate limiting decorator
def rate_limit(limit=5, window=60):
    """
    Simple in-memory rate limiting decorator
    limit: maximum requests per window
    window: time window in seconds
    """
    storage = {}
    
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            current_time = int(os.urandom(1)[0])  # Mock time for example
            
            # Initialize or cleanup expired entries
            if client_ip not in storage:
                storage[client_ip] = []
            storage[client_ip] = [t for t in storage[client_ip] if current_time - t < window]
            
            # Check if limit exceeded
            if len(storage[client_ip]) >= limit:
                return jsonify({"error": "Rate limit exceeded. Try again later."}), 429
            
            # Add current request timestamp
            storage[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# API documentation route
@app.route('/', methods=['GET'])
def api_docs():
    return jsonify({
        "api_name": "Decryption API",
        "version": "2.0",
        "endpoints": [
            {
                "path": "/decrypt-latest",
                "method": "GET",
                "description": "Decrypts AES encrypted content provided as base64",
                "parameters": [
                    {
                        "name": "content",
                        "in": "query",
                        "required": True,
                        "description": "Base64 encoded encrypted content"
                    }
                ]
            }
        ]
    }), 200

# API route to decrypt content from query parameter
@app.route('/decrypt-latest', methods=['GET'])
@rate_limit(limit=10, window=60)  # 10 requests per minute
def decrypt_latest():
    try:
        # Retrieve the encrypted content from the query parameter
        encrypted_content = request.args.get('content')
        if not encrypted_content:
            return jsonify({
                "error": "No encrypted content provided",
                "usage": "Use ?content=<BASE64_ENCODED_ENCRYPTED_TEXT>"
            }), 400

        # Decode base64 and decrypt the content
        try:
            ciphertext = base64.b64decode(encrypted_content)
        except Exception:
            return jsonify({"error": "Invalid base64 encoding"}), 400

        try:
            decrypted_text = decrypt_aes_ecb_128(ciphertext, KEY)
        except Exception as e:
            return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

        # Format the decrypted content
        try:
            formatted_text = format_decrypted_content(decrypted_text)
        except Exception as e:
            formatted_text = "Formatting failed, returning raw output"

        # Return the JSON response with both the original and formatted decrypted content
        return jsonify({
            "message": Ezxx + formatted_text,
            "decrypted_content": decrypted_text.decode('utf-8', errors='replace'),
            "beautiful_decrypted_content": formatted_text
        }), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Special handler for Vercel serverless function
def handler(request, context):
    """Handle a request to the function."""
    with app.test_client() as client:
        response = client.get(request.path, 
                             query_string=request.args, 
                             headers=request.headers)
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True)
        }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
