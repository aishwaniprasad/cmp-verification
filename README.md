# CMP Verification

A project that verifies college students by email OTP and then sends them a WhatsApp invite to the college group.

## How it works

1. A student enters their name, roll number, college email and phone number.
2. The backend sends an OTP to their college email.
3. After the student enters the correct OTP, the WhatsApp bot sends them the group invite link.

## Tech used

- **Backend:** Python, FastAPI, PostgreSQL
- **WhatsApp bot:** Node.js, whatsapp-web.js

## Project structure

- `backend/` - FastAPI server (OTP and verification logic)
- `whatsapp-service/` - WhatsApp bot that sends the invite

## How to run

**Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env`, fill in your values, then run:
```
uvicorn main:app --reload
```

**WhatsApp bot**
```
cd whatsapp-service
npm install
npm start
```
Scan the QR code with WhatsApp when it appears.

## Status

Work in progress. Email OTP currently prints to the console instead of sending a real email.
