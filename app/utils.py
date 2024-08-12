import os
import glob
import shutil

from .config import BASE_PATH, COMMERCIAL_OFFER_PATH
from .logger import logging
from fastapi import HTTPException, UploadFile, File, Form


def get_id_pattern(company_id: str) -> str:
    return os.path.join(BASE_PATH, f"*(id_{company_id})*")


def create_company_folder(company_name: str, company_id: str, dl_number: str) -> str:
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

    return main_dir


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


def update_to_archive_company_folder(company_id: str, dl_number: str) -> str:
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
                return new_folder_path
    except PermissionError as e:
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def update_to_active_company_folder(company_id: str, dl_number: str) -> str:
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
                return new_folder_path
    except PermissionError as e:
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def copy_comm_offer_to_folder(company_id: str, file_path: str) -> None:
    """Копирует коммерческое предложение в папку сделки"""

    pattern: str = get_id_pattern(company_id)
    found: bool = False

    try:
        for folder_path in glob.glob(pattern, recursive=True):
            if os.path.isdir(folder_path):
                folder_name = os.path.basename(folder_path)
                parent_dir = os.path.dirname(folder_path)
                commercial_offer_path = os.path.join(
                    parent_dir, folder_name, "Расчет и КП"
                )

                # Нужно убедиться, что папка назначения существует
                os.makedirs(commercial_offer_path, exist_ok=True)

                # Получаем оригинальное имя файла из переданного пути
                original_filename = os.path.basename(file_path)

                # Формируем целевой путь для копирования файла
                destination_file_path = os.path.join(
                    commercial_offer_path, original_filename
                )

                logging.info(f"Copying {original_filename} to {destination_file_path}")

                # Копируем файл в целевую папку
                shutil.copy(file_path, destination_file_path)

                logging.info(
                    f"Successfully copied {original_filename} to {destination_file_path}"
                )
                found = True
                break

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        raise e

    if not found:
        logging.info(f"Папка с id_{company_id} не найдена.")
        raise HTTPException(
            status_code=404, detail=f"Папка с id_{company_id} не найдена."
        )


def create_comm_offer(file: UploadFile = File(...), user_login: str = Form(...)) -> str:
    """Создает коммерческое предложение"""

    user_directory = os.path.join(COMMERCIAL_OFFER_PATH, user_login)
    path_to_offer = os.path.join(user_directory, file.filename)

    try:
        # Создание директории, если она не существует
        os.makedirs(user_directory, exist_ok=True)

        # Сохранение файла
        with open(path_to_offer, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except OSError as e:
        # Обработка ошибок, связанных с файловой системой
        raise HTTPException(status_code=500, detail=f"Ошибка при создании файла: {e}")

    except Exception as e:
        # Обработка других непредвиденных ошибок
        raise HTTPException(status_code=500, detail=f"Произошла ошибка: {e}")

    return path_to_offer
