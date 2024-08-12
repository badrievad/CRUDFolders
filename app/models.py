from pydantic import BaseModel


class Company(BaseModel):
    company_name: str
    company_id: str
    dl_number: str


class Dl(BaseModel):
    dl_number: str


class CommercialOffer(BaseModel):
    company_id: str
    file_path: str


class PathToOffer(BaseModel):
    file_path: str
