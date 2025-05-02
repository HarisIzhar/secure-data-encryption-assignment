import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Generate key (should be stored securely in production)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# In-memory storage
stored_data = {}
failed_attempts = st.session_state.get("failed_attempts", 0)

# Hash function
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Encrypt function
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Decrypt function
def decrypt_data(encrypted_text, passkey):
    global stored_data
    hashed_passkey = hash_passkey(passkey)
    for key, value in stored_data.items():
        if key == encrypted_text and value["passkey"] == hashed_passkey:
            st.session_state["failed_attempts"] = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    st.session_state["failed_attempts"] = st.session_state.get("failed_attempts", 0) + 1
    return None

# UI setup
st.title("🔒 Secure Data Encryption System")
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")
    user_data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")
    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed = hash_passkey(passkey)
            encrypted = encrypt_data(user_data)
            stored_data[encrypted] = {"encrypted_text": encrypted, "passkey": hashed}
            st.success("✅ Data stored securely!")
            st.code(encrypted, language="text")
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")
    encrypted_text = st.text_area("Enter Encrypted Data:")
    passkey = st.text_input("Enter Passkey:", type="password")
    if st.button("Decrypt"):
        if encrypted_text and passkey:
            result = decrypt_data(encrypted_text, passkey)
            if result:
                st.success(f"✅ Decrypted Data: {result}")
            else:
                remaining = 3 - st.session_state.get("failed_attempts", 0)
                st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")
                if st.session_state["failed_attempts"] >= 3:
                    st.warning("🔒 Too many failed attempts! Redirecting to Login Page...")
                    st.experimental_rerun()
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")
    login_pass = st.text_input("Enter Master Password:", type="password")
    if st.button("Login"):
        if login_pass == "admin123":
            st.session_state["failed_attempts"] = 0
            st.success("✅ Reauthorized successfully!")
        else:
            st.error("❌ Incorrect password!")