import random
import os
import httpx
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db, Student
from schemas import OTPRequest, OTPVerify

load_dotenv()

app = FastAPI(title="College Verification Backend")

COLLEGE_DOMAIN = os.getenv("COLLEGE_DOMAIN", "@college.ac.in")
WHATSAPP_SERVICE_URL = os.getenv("WHATSAPP_SERVICE_URL", "http://localhost:3000/add-member")
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID")

def send_email_otp(to_email: str, otp: str):
    print(f"[EMAIL SERVICE] Sent OTP code '{otp}' to {to_email}")

async def call_whatsapp_bot(phone_number: str):
    clean_phone = "".join(filter(str.isdigit, phone_number))
    payload = {
        "phoneNumber": clean_phone,
        "groupId": WHATSAPP_GROUP_ID
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(WHATSAPP_SERVICE_URL, json=payload, timeout=15.0)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to communicate with WhatsApp service: {e}")
            return None

@app.post("/api/send-otp")
def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    if not request.email.endswith(COLLEGE_DOMAIN):
        raise HTTPException(
            status_code=400, 
            detail=f"Only email addresses ending with {COLLEGE_DOMAIN} are allowed."
        )

    existing = db.query(Student).filter(Student.email == request.email).first()
    if existing and existing.is_verified:
        raise HTTPException(status_code=400, detail="This college email is already verified.")

    otp = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    if not existing:
        student = Student(
            full_name=request.full_name,
            roll_number=request.roll_number,
            email=request.email,
            phone_number=request.phone_number,
            otp_code=otp,
            otp_expires_at=expires_at
        )
        db.add(student)
    else:
        existing.otp_code = otp
        existing.otp_expires_at = expires_at
        existing.phone_number = request.phone_number

    db.commit()

    send_email_otp(request.email, otp)
    return {"status": "success", "message": "OTP sent to your college email."}

@app.post("/api/verify-otp")
async def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == request.email).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")

    if student.otp_code != request.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code entered.")

    if datetime.utcnow() > student.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired. Request a new one.")

    student.is_verified = True
    student.otp_code = None
    db.commit()

    wa_result = await call_whatsapp_bot(student.phone_number)

    return {
        "status": "success", 
        "message": "OTP verified successfully!",
        "whatsapp_result": wa_result
    }

    if __name__ == "__main__":
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)