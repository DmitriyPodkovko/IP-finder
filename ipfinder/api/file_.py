import logging
from typing import List

from asgiref.sync import sync_to_async
from django.http import HttpRequest
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

from db.executor import DBExecutor
from excel.handler import ExcelHandler

async_api = NinjaAPI(
    title="Async API",
    description="Async API for Upload/Download files.xlsx/csv",
    version="1.0.0",
    urls_namespace="api-file-handlers",
    openapi_url="documentation/openapi.json",
    docs_url="docs/",
)

db_executor = DBExecutor()
connect_on = sync_to_async(db_executor.connect_on)
execute = sync_to_async(db_executor.execute)
connect_off = sync_to_async(db_executor.connect_off)


@async_api.post("/files", url_name="api-file-handlers")
async def upload_(
        request: HttpRequest, files: List[UploadedFile] = File(...)):
    all_warning_numbers = set()
    for f in files:
        excel_handler = ExcelHandler(f)
        get_ip_list_from_xlsx_file = sync_to_async(excel_handler.get_ip_list_from_xlsx_file)
        ip_list = await get_ip_list_from_xlsx_file()
        create_output_xlsx_file = sync_to_async(excel_handler.create_output_xlsx_file)
        await create_output_xlsx_file()
        if await connect_on():
            for i in ip_list:
                DST_numbers = await execute(i)
                logging.info(f'response: {DST_numbers}')
                if DST_numbers:
                    warning_numbers = db_executor.execute_check_numbers(DST_numbers)
                    if warning_numbers:
                        all_warning_numbers |= warning_numbers
                        logging.info(f'!!! WARNING NUMBERS: {warning_numbers} !!!')
                save_result_to_output_xlsx_file = sync_to_async(excel_handler.save_result_to_output_xlsx_file)
                await save_result_to_output_xlsx_file(DST_numbers)
            await connect_off()
    if all_warning_numbers:
        return {"status": "OK",
                "WARNING NUMBERS": f"{all_warning_numbers}"}
    else:
        return {"status": "OK"}


