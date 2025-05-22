from flask import Flask, render_template, request, send_file, flash
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
import base64

app = Flask(__name__)
app.secret_key = get_random_bytes(16)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def encrypt_file(file_data, key):
    # Convert key to 32 bytes (256 bits) using SHA-256
    from hashlib import sha256
    key = sha256(key.encode()).digest()
    
    # Generate random IV
    iv = get_random_bytes(16)
    
    # Create cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the data and encrypt
    padded_data = pad(file_data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # Combine IV and encrypted data
    return iv + encrypted_data

def decrypt_file(encrypted_data, key):
    # Convert key to 32 bytes (256 bits) using SHA-256
    from hashlib import sha256
    key = sha256(key.encode()).digest()
    
    # Extract IV and encrypted data
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    
    # Create cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt and unpad
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data, AES.block_size)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('index.html')
        
        file = request.files['file']
        key = request.form.get('key', '')
        operation = request.form.get('operation', '')
        
        if file.filename == '':
            flash('No file selected')
            return render_template('index.html')
        
        if not key:
            flash('Please enter a key')
            return render_template('index.html')
        
        # Read file data
        file_data = file.read()
        
        try:
            if operation == 'encrypt':
                # Encrypt file
                encrypted_data = encrypt_file(file_data, key)
                output_filename = f"encrypted_{file.filename}"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(encrypted_data)
                
                return send_file(output_path, as_attachment=True, download_name=output_filename)
            
            elif operation == 'decrypt':
                # Decrypt file
                decrypted_data = decrypt_file(file_data, key)
                output_filename = f"decrypted_{file.filename}"
                output_path = os.path.join(UPLOAD_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
                
                return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            if 'Padding is incorrect' in str(e):
                flash('Sai rồi, vui lòng thử lại đi')
            else:
                flash(f'Lỗi: {str(e)}')
            return render_template('index.html')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 