import os
from typing import List, Tuple, Any
import openpyxl
import logging
from openpyxl.styles import NamedStyle
from config.handler_settings import (EXCEL_ROW_COLUMN,
                                     DESTINATION_NUMBER,
                                     EXCEL_OUTPUT_FILE_PREFIX,
                                     RESULT_DIRECTORY)


class ExcelHandler:
    def __init__(self, xlsx_file) -> None:
        self._xlsx_file = xlsx_file
        # self._cell_style = None
        self._DST_column_idx = None
        self._xlsx_output_file = None
        self._current_row = EXCEL_ROW_COLUMN.get('default').get('Start_row')
        self.errors = ''

    def get_ip_list_from_xlsx_file(self) -> list[tuple[Any, Any, Any, Any, Any]] | list[Any]:
        try:
            ip_list = []
            workbook = openpyxl.load_workbook(self._xlsx_file)
            sheet = workbook.active
            for row in sheet.iter_rows(min_row=EXCEL_ROW_COLUMN.get('default').get('Start_row'), values_only=True):
                ip_tuple = (
                    row[EXCEL_ROW_COLUMN.get('default').get('IP_DST')],
                    row[EXCEL_ROW_COLUMN.get('default').get('Port_DST')],
                    row[EXCEL_ROW_COLUMN.get('default').get('Date')],
                    row[EXCEL_ROW_COLUMN.get('default').get('Time')],
                    row[EXCEL_ROW_COLUMN.get('default').get('Provider')]
                )
                # Check if all elements in the tuple are not empty
                if all(ip_tuple):
                    ip_list.append(ip_tuple)
                    logging.info(f'IP_DST, Port_DST, Date, Time, Provider: {ip_tuple}')
            workbook.close()
            return ip_list
        except Exception as e:
            logging.error(f'Error input .xlsx file:\n {self._xlsx_file} ({str(e)})')
            self.errors += 'get xlsx error\n'
            return []

    def create_output_xlsx_file(self, user_directory) -> None:
        try:
            workbook = openpyxl.load_workbook(self._xlsx_file)
            sheet = workbook.active
            # self._cell_style = NamedStyle(name='cell_style')
            # self._cell_style.font = sheet.cell(row=1, column=1).font.copy()
            # self._cell_style.border = sheet.cell(row=1, column=1).border.copy()
            if EXCEL_ROW_COLUMN.get('default').get('DST') >= 0:
                self._DST_column_idx = EXCEL_ROW_COLUMN.get('default').get('DST') + 1
            else:
                self._DST_column_idx = sheet.max_column + 1
                sheet.cell(row=1, column=self._DST_column_idx, value=DESTINATION_NUMBER)
            file_name, file_extension = os.path.splitext(self._xlsx_file.name)
            self._xlsx_output_file = f'{user_directory}/{file_name}{EXCEL_OUTPUT_FILE_PREFIX}.xlsx'
            workbook.save(self._xlsx_output_file)
            workbook.close()
            logging.info(f'CREATED: {self._xlsx_output_file}')
        except Exception as e:
            logging.error(f'Error creating .xlsx file:\n {self._xlsx_file} ({str(e)})')
            self.errors += 'create xlsx error\n'

    def save_result_to_output_xlsx_file(self, dst_list: list) -> None:
        try:
            workbook = openpyxl.load_workbook(self._xlsx_output_file)
            sheet = workbook.active
            for dst_set in dst_list:
                current_column_idx = self._DST_column_idx
                for number in dst_set:
                    sheet.cell(row=self._current_row, column=current_column_idx, value=number)
                    # There is a bug in the library with style assignment
                    # new_cell.style = self._cell_style
                    current_column_idx += 1
                self._current_row += 1
            workbook.save(self._xlsx_output_file)
            workbook.close()
            logging.info(f'saved')
        except Exception as e:
            logging.error(f'Error saving .xlsx:\n {self._xlsx_file} ({str(e)})')
            self.errors += 'save xlsx error\n'
