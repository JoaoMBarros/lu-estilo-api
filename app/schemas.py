import re
from pydantic import BaseModel

class Client(BaseModel):
    name: str
    email: str
    cpf: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")
    
    def validate_cpf(self):
        if not re.match(r"\d{11}", self.cpf):
            raise ValueError("Invalid CPF")
    
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

class User(BaseModel):
    name: str
    email: str
    password: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")
   
    def validate_name(self):
        if not re.match(r"[a-zA-Z\s]+", self.name):
            raise ValueError("Invalid name")

class UserLogin(BaseModel):
    email: str
    password: str

    def validate_email(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Invalid email")