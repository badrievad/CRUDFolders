import os
import glob
import shutil

from .config import BASE_PATH
from .logger import logging
from fastapi import HTTPException


def get_id_pattern(company_id: str) -> str:
    return os.path.join(BASE_PATH, f"*(id_{company_id})*")


def create_company_folder(company_name: str, company_id: str, dl_number: str) -> None:
    """Создает папку для сделки с id_{company_id}"""
    main_dir: str = os.path.join(
        BASE_PATH, f"{dl_number} {company_name} (id_{company_id})"
    )
    os.makedirs(main_dir, exist_ok=True)

    logging.info(f"Папка {main_dir} успешно создана.")

    subdirectories: list = [
        "БКИ",
        "Договоры",
        "Документы клиента",
        "Документы продавца",
        "Заключение",
        "Расчет и КП",
    ]

    for subdirectory in subdirectories:
        os.makedirs(os.path.join(main_dir, subdirectory), exist_ok=True)


def delete_company_folder(company_id: str) -> None:
    """Удаляет папку сделки с id_{company_id}"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    try:
        for folder_path in glob.glob(pattern, recursive=True):
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                logging.info(f"Папка {folder_path} успешно удалена.")
                found = True
                break
    except PermissionError as e:
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def update_to_archive_company_folder(company_id: str, dl_number: str) -> None:
    """Добавляет в название папки тег (Архив)"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    try:
        for folder_path in glob.glob(pattern, recursive=True):
            if os.path.isdir(folder_path):
                folder_name = os.path.basename(folder_path)
                parent_dir = os.path.dirname(folder_path)
                logging.info(folder_name)
                logging.info(dl_number)
                new_folder_name = f"(Архив){folder_name.replace(dl_number, '')}"
                new_folder_path = os.path.join(parent_dir, new_folder_name)
                os.rename(folder_path, new_folder_path)
                logging.info(
                    f"Папка {folder_path} успешно обновлена до {new_folder_path}."
                )
                found = True
                break
    except PermissionError as e:
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def update_to_active_company_folder(company_id: str, dl_number: str) -> None:
    """Удаляет из названия папки тег (Архив)"""
    pattern: str = get_id_pattern(company_id)
    found: bool = False
    try:
        for folder_path in glob.glob(pattern, recursive=True):
            if os.path.isdir(folder_path):
                folder_name = os.path.basename(folder_path)
                parent_dir = os.path.dirname(folder_path)
                new_folder_name = f"{dl_number} {folder_name.replace("(Архив) ", "")}"
                new_folder_path = os.path.join(parent_dir, new_folder_name)
                os.rename(folder_path, new_folder_path)
                logging.info(
                    f"Папка {folder_path} успешно обновлена до {new_folder_path}."
                )
                found = True
                break
    except PermissionError as e:
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )
