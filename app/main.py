from .logger import logging

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

from .models import Company, Dl
from .utils import (
    create_company_folder,
    delete_company_folder,
    update_to_archive_company_folder,
    update_to_active_company_folder,
    copy_comm_offer_to_folder,
    create_comm_offer,
)


app = FastAPI()


@app.post("/create")
def create_folder(company: Company) -> dict[str, str]:
    create_company_folder(company.company_name, company.company_id, company.dl_number)
    return {"message": "Папка успешно создана."}


@app.delete("/delete/{company_id}")
def delete_folder(company_id: str) -> dict[str, str]:
    delete_company_folder(company_id)
    return {"message": "Папка успешно удалена."}


@app.put("/archive/{company_id}")
def archive_folder(company_id: str, dl: Dl) -> dict[str, str]:
    update_to_archive_company_folder(company_id, dl.dl_number)
    return {"message": "Папка успешно обновлена до архива."}


@app.put("/activate/{company_id}")
def activate_folder(company_id: str, dl: Dl) -> dict[str, str]:
    update_to_active_company_folder(company_id, dl.dl_number)
    return {"message": "Папка успешно обновлена до активного состояния."}


@app.get("/is_available")
def is_available() -> JSONResponse:
    try:
        service_available = True
        return JSONResponse(content={"available": service_available}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"available": False, "error": str(e)}, status_code=500
        )


@app.post("/commercial-offer/upload")
def upload_commercial_offer(
    company_id: str = Form(...), file: UploadFile = File(...)
) -> dict[str, str]:
    logging.info(f"Company ID: {company_id}")
    logging.info(f"File: {file.filename}")
    copy_comm_offer_to_folder(company_id, file)
    return {"message": "File uploaded successfully"}


@app.post("/commercial-offer/create")
def create_commercial_offer(
    file: UploadFile = File(...), user_login: str = Form(...)
) -> dict[str, str]:
    path_to_offer: str = create_comm_offer(file, user_login)
    response = {"message": "File created successfully", "path_to_file": path_to_offer}
    return response
