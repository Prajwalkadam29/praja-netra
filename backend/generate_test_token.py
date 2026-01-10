from app.services.auth_service import auth_service
from app.config import settings

# This generates a token for a test email.
# Make sure this email exists in your 'users' table or create it.
test_email = "testuser@example.com"
token = auth_service.create_access_token(data={"sub": test_email})

print(f"--- YOUR TEST JWT ---")
print(token)
print(f"----------------------")