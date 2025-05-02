from pydantic import BaseModel, EmailStr, field_validator, Field
import re


password_regex = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!.%*#?&])[A-Za-z\d@$!%*#?.&]{6,25}$")


class UserCreate(BaseModel):
    username: str = Field()
    password: str = Field()
    email: EmailStr = Field(max_length=128)

    @field_validator('username')
    def username_validator(cls, value):
        if len(value) not in range(2, 30):
            raise ValueError("Username requirements: 2-30 characters")
        return value

    @field_validator('password')
    def password_validator(cls, value):
        if not password_regex.match(value):
            raise ValueError(
                'Password requirements: 6-25 characters, at least 1 letter, digit, special character - (@$!.%*#?&)')
        return value


class UserLogin(BaseModel):
    password: str = Field()
    email: str = Field()
    referer: str

    @field_validator('email')
    def email_validator(cls, email):
        if len(email) not in range(1, 128):
            raise ValueError('Invalid e-mail format')
        return email

    @field_validator('password')
    def password_validator(cls, password):
        if len(password) not in range(1, 30):
            raise ValueError('Invalid password format')
        return password


class UserInfo(BaseModel):
    username: str = Field()
    email: str = Field()
    id: int = Field()

    @field_validator('email')
    def email_validator(cls, email):
        if len(email) not in range(1, 128):
            raise ValueError('Invalid e-mail format')
        return email

    @field_validator('username')
    def username_validator(cls, value):
        if len(value) not in range(3, 30):
            raise ValueError("Username: 3-30 characters")
        return value


class ResetPasswordData(BaseModel):
    new_password: str = Field()
    user_email: str = Field()
    reset_pw_token: str = Field()

    @field_validator('user_email')
    def email_validator(cls, email):
        if len(email) not in range(1, 128):
            raise ValueError('Invalid e-mail format')
        return email

    @field_validator('new_password')
    def password_validator(cls, value):
        if not password_regex.match(value):
            raise ValueError(
                'Password: 6-25 characters, at least 1 letter, digit, special character - (@$!.%*#?&)')
        return value

