from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from .logger import logging
from .models import Company, Dl, CommercialOffer, PdfPath
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
    path_to_folder = create_company_folder(
        company.company_name, company.company_id, company.dl_number
    )
    return {"message": "Папка успешно создана.", "path_to_folder": path_to_folder}


@app.delete("/delete/{company_id}")
def delete_folder(company_id: str) -> dict[str, str]:
    delete_company_folder(company_id)
    return {"message": "Папка успешно удалена."}


@app.put("/archive/{company_id}")
def archive_folder(company_id: str, dl: Dl) -> dict[str, str]:
    path_to_offer = update_to_archive_company_folder(company_id, dl.dl_number)
    return {
        "message": "Папка успешно обновлена до архива.",
        "path_to_folder": path_to_offer,
    }


@app.put("/activate/{company_id}")
def activate_folder(company_id: str, dl: Dl) -> dict[str, str]:
    path_to_offer = update_to_active_company_folder(company_id, dl.dl_number)
    return {
        "message": "Папка успешно обновлена до активного состояния.",
        "path_to_folder": path_to_offer,
    }


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
def upload_commercial_offer(offer: CommercialOffer) -> dict[str, str]:
    logging.info(f"Company ID: {offer.company_id}")
    logging.info(f"Xlsx path: {offer.xlsx_path}")
    logging.info(f"Pdf path: {offer.pdf_path}")
    copy_comm_offer_to_folder(offer.company_id, offer.xlsx_path, offer.pdf_path)
    return {"message": "Files uploaded successfully"}


@app.post("/commercial-offer/create")
def create_commercial_offer(
    file: UploadFile = File(...), user_login: str = Form(...)
) -> dict[str, str]:
    path_to_xlsx: str = create_comm_offer(file, user_login)
    response = {"message": "File created successfully", "path_to_xlsx": path_to_xlsx}
    return response


@app.post("/commercial-offer/download")
def download_commercial_offer(pdf: PdfPath) -> FileResponse:
    # Создаем объект Path
    file_path = Path(pdf.path)

    # Проверяем, существует ли файл
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Извлекаем имя файла
    file_name = file_path.name

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=file_name,
    )
