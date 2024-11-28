from flask import Flask, request, jsonify
import base64
from Crypto.Cipher import AES
import json

app = Flask(__name__)

# Constants
BASE64_KEY = "X25ldHN5bmFfbmV0bW9kXw=="
KEY = base64.b64decode(BASE64_KEY)
Ezxx = "This Script Generated By : EstebanZxx\nBeta Test Module : V1\n=====================================\nResult Decrypt : \n"

# Decrypt function using AES ECB mode
def decrypt_aes_ecb_128(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.rstrip(b"\x00")  # Remove trailing null bytes

# Function to format decrypted content
def format_decrypted_content(decrypted_text):
    try:
        # Attempt to parse the decrypted text as JSON
        data = json.loads(decrypted_text)
        formatted_text = ""
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    formatted_text += f"{sub_key} {sub_value}\n"
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for sub_key, sub_value in item.items():
                            formatted_text += f"{sub_key} {sub_value}\n"
                    else:
                        formatted_text += f"{key} {item}\n"
            else:
                formatted_text += f"{key} {value}\n"
        return formatted_text
    except json.JSONDecodeError:
        # If not JSON, return the original decrypted text
        return decrypted_text.decode('utf-8')

# API route to decrypt content from query parameter
@app.route('/decrypt-latest', methods=['GET'])
def decrypt_latest():
    try:
        # Retrieve the encrypted content from the query parameter
        encrypted_content = request.args.get('content')
        if not encrypted_content:
            return jsonify({"error": "No encrypted content provided. Use ?content=<BASE64_ENCODED_ENCRYPTED_TEXT>"}), 400

        # Decode base64 and decrypt the content
        ciphertext = base64.b64decode(encrypted_content)
        decrypted_text = decrypt_aes_ecb_128(ciphertext, KEY)

        # Format the decrypted content
        formatted_text = format_decrypted_content(decrypted_text)

        return jsonify({
            "message": Ezxx + formatted_text,
            "decrypted_content": formatted_text
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
