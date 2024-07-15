from pydantic import BaseModel


class Company(BaseModel):
    company_name: str
    company_id: str
    dl_number: str


class Dl(BaseModel):
    dl_number: str
