from app.services.auth_service import auth_service
# Match the email exactly as it is in your DB
token = auth_service.create_access_token(data={"sub": "admin@prajanetra.gov.in"})
print(f"\nYour JWT Token:\n{token}\n")
