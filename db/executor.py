import logging
import cx_Oracle
from django.db import connections
from datetime import datetime

from config.settings import ORACLE_FUNCTIONS, INNER_IPS, OPERATORS

cx_Oracle.init_oracle_client(lib_dir="/Users/dmitriypodkovko/Downloads/instantclient_19_8")

# for deploy
# cx_Oracle.init_oracle_client(lib_dir="/usr/lib/oracle/21/client64/lib")


class DBExecutor:
    def __init__(self) -> None:
        self._cursor = None
        self._ip_tuple = None
        logging.info(f'init DBExecutor')

    def connect_on(self) -> bool:
        try:
            self._cursor = connections['filter'].cursor()
            logging.info(f'CONNECT ON')
            return True
        except Exception as e:
            logging.error(f'DB error connect on:\n {str(e)}')
            return False

    def connect_off(self) -> None:
        try:
            self._cursor.close()
            logging.info(f'CONNECT OFF')
        except Exception as e:
            logging.error(f'DB error connect off:\n {str(e)}')

    def execute(self, ip_tuple: tuple) -> set:
        try:
            logging.info(f'aaaaaaaa')
            result = set()
            self._ip_tuple = ip_tuple
            ip = self._ip_tuple[0]
            port = self._ip_tuple[1]
            first_part_ip = int(ip.split('.', 1)[0])
            operator = OPERATORS.get(self._ip_tuple[4])
            dt = datetime.strptime(self._ip_tuple[2] + ' ' + self._ip_tuple[3],
                                   '%d.%m.%Y %H:%M:%S')
            logging.info(f'bbbbbbbbbb')
            if first_part_ip in INNER_IPS:
                logging.info(f'ccccccccccccc inner_tel_func')
                oracle_func = ORACLE_FUNCTIONS.get('inner_tel_func')
                ref_cursor = self._cursor.callfunc(oracle_func, cx_Oracle.CURSOR,
                                                   [ip, operator, dt])
                logging.info(f'ddddddddddddd')
            else:
                logging.info(f'ccccccccccccc tel_func')
                oracle_func = ORACLE_FUNCTIONS.get('tel_func')
                ref_cursor = self._cursor.callfunc(oracle_func, cx_Oracle.CURSOR,
                                                   [ip, port, operator, dt])
                logging.info(f'dddddddddddddddddfffffffffffff')
            logging.info(f'{oracle_func}, {ip}, {port}, {operator}, {dt}')
            if ref_cursor:
                for row in ref_cursor.fetchall():
                    for i in row:
                        result.add(i)
            return result
        except Exception as e:
            logging.error(f'DB error execute:\n {str(e)}')
            return {'380000000000'}
