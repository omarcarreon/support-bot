import secrets
import base64

# Generate a secure random key
random_bytes = secrets.token_bytes(32)
secret_key = base64.b64encode(random_bytes).decode('utf-8')

print("\nGenerated Secret Key:")
print("-" * 50)
print(secret_key)
print("-" * 50)
print("\nYou can copy this key and use it as your SECRET_KEY in the .env file") 