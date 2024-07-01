from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import BASE_PATH
from .logger import logging

import glob
import os
import shutil

app = FastAPI()


class Company(BaseModel):
    company_name: str
    company_id: str


def get_id_pattern(company_id: str) -> str:
    return os.path.join(BASE_PATH, f"*(id_{company_id})*")


def create_company_folder(company_name: str, company_id: str) -> None:
    """Создает папку для сделки с id_{company_id}"""
    main_dir: str = os.path.join(BASE_PATH, f"{company_name} (id_{company_id})")
    os.makedirs(main_dir, exist_ok=True)

    subdirectories: list = [
        "БКИ",
        "Договоры",
        "Документы клиента",
        "Документы продавца",
        "Заключение",
        "Расчет",
    ]

    for subdirectory in subdirectories:
        os.makedirs(os.path.join(main_dir, subdirectory), exist_ok=True)


def delete_company_folder(company_id: str) -> None:
    """Удаляет папку сделки с id_{company_id}"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    for folder_path in glob.glob(pattern, recursive=True):
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            logging.info(f"Папка {folder_path} успешно удалена.")
            found = True
            break

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def update_to_archive_company_folder(company_id: str) -> None:
    """Добавляет в название папки тег (Архив)"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    for folder_path in glob.glob(pattern, recursive=True):
        if os.path.isdir(folder_path):
            folder_name = os.path.basename(folder_path)
            parent_dir = os.path.dirname(folder_path)
            new_folder_name = f"(Архив) {folder_name}"
            new_folder_path = os.path.join(parent_dir, new_folder_name)
            os.rename(folder_path, new_folder_path)
            logging.info(f"Папка {folder_path} успешно обновлена до {new_folder_path}.")
            found = True
            break

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def update_to_active_company_folder(company_id: str) -> None:
    """Удаляет из названия папки тег (Архив)"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    for folder_path in glob.glob(pattern, recursive=True):
        if os.path.isdir(folder_path):
            folder_name = os.path.basename(folder_path)
            parent_dir = os.path.dirname(folder_path)
            new_folder_name = folder_name.replace("(Архив) ", "")
            new_folder_path = os.path.join(parent_dir, new_folder_name)
            os.rename(folder_path, new_folder_path)
            logging.info(f"Папка {folder_path} успешно обновлена до {new_folder_path}.")
            found = True
            break

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


@app.post("/create")
def create_folder(company: Company) -> dict[str, str]:
    create_company_folder(company.company_name, company.company_id)
    return {"message": "Папка успешно создана."}


@app.delete("/delete/{company_id}")
def delete_folder(company_id: str) -> dict[str, str]:
    delete_company_folder(company_id)
    return {"message": "Папка успешно удалена."}


@app.put("/archive/{company_id}")
def archive_folder(company_id: str) -> dict[str, str]:
    update_to_archive_company_folder(company_id)
    return {"message": "Папка успешно обновлена до архива."}


@app.put("/activate/{company_id}")
def activate_folder(company_id: str) -> dict[str, str]:
    update_to_active_company_folder(company_id)
    return {"message": "Папка успешно обновлена до активного состояния."}
