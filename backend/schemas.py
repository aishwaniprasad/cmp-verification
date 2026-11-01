import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class OTPRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Full Name")
    roll_number: str = Field(
        ...,
        description="Roll Number format: YYYYBBBXXXX",
    )
    email: EmailStr = Field(
        ...,
        description="College Email ID",
        examples=["student@nsut.ac.in"]
    )
    phone_number: str = Field(
        ...,
        description="10-digit phone number",
    )

    @field_validator("roll_number")
    @classmethod
    def validate_roll_number(cls, v: str) -> str:
        v = v.strip().upper()
        pattern = r"^\d{4}[A-Z]{3}\d{4}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Invalid Roll Number format. It must be 4-digit year + 3-letter branch + 4-digit roll number."
            )
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v.strip())

        if re.match(r"^[6-9]\d{9}$", cleaned):
            cleaned = f"+91{cleaned}"
        elif re.match(r"^91[6-9]\d{9}$", cleaned):
            cleaned = f"+{cleaned}"
        if not re.match(r"^\+91[6-9]\d{9}$", cleaned):
            raise ValueError(
                "Invalid Phone Number. Enter a valid 10-digit Indian mobile number."
            )

        return cleaned


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)