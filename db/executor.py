import logging
import cx_Oracle
from django.db import connections
from datetime import datetime
from config.settings import (ORACLE_FUNCTIONS,
                             OPERATORS,
                             MOB3_INNER_IPS,
                             MTS_INNER_IPS,
                             KS_INNER_IPS,
                             LIFE_INNER_IPS)


# for development
cx_Oracle.init_oracle_client(lib_dir="/Users/dmitriypodkovko/Downloads/instantclient_19_8")


class DBExecutor:
    def __init__(self) -> None:
        self._cursor = None
        self._ip_tuple = None
        # logging.info(f'init DBExecutor')

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
            result = set()
            self._ip_tuple = ip_tuple
            ip = self._ip_tuple[0]
            port = self._ip_tuple[1]
            first_part_ip = int(ip.split('.', 1)[0])
            operator = OPERATORS.get(self._ip_tuple[4])
            dt = datetime.strptime(self._ip_tuple[2] + ' ' + self._ip_tuple[3],
                                   '%d.%m.%Y %H:%M:%S')
            checkout = CheckoutInnerIP(first_part_ip, operator)
            if checkout.check_inner():
                oracle_func = ORACLE_FUNCTIONS.get('inner_tel_func')
                logging.info(f'{oracle_func}, {ip}, {operator}, {dt}')
                ref_cursor = self._cursor.callfunc(oracle_func, cx_Oracle.CURSOR,
                                                   [ip, operator, dt])
                logging.info(f'request done')
            else:
                oracle_func = ORACLE_FUNCTIONS.get('tel_func')
                logging.info(f'{oracle_func}, {ip}, {port}, {operator}, {dt}')
                ref_cursor = self._cursor.callfunc(oracle_func, cx_Oracle.CURSOR,
                                                   [ip, port, operator, dt])
                logging.info(f'request done')
            if ref_cursor:
                for row in ref_cursor.fetchall():
                    for i in row:
                        result.add(i)
            return result
        except Exception as e:
            logging.error(f'DB error execute:\n {str(e)}')
            return {'380000000000'}


class CheckoutInnerIP:

    def __init__(self, first_part_ip, operator):
        self._first_part_ip = first_part_ip
        self._operator = operator

    def check_inner(self):
        default = 'Incorrect operator'
        return getattr(self, f'_case_{self._operator}', lambda: default)()

    def _case_3MOB(self) -> bool:
        if self._first_part_ip in MOB3_INNER_IPS:
            logging.info(f'_case_3MOB for inner func -> True')
            return True
        return False

    def _case_MTS(self) -> bool:
        if self._first_part_ip in MTS_INNER_IPS:
            logging.info(f'_case_MTS for inner func -> True')
            return True
        return False

    def _case_KS(self) -> bool:
        if self._first_part_ip in KS_INNER_IPS:
            logging.info(f'_case_KS for inner func -> True')
            return True
        return False

    def _case_LIFE(self) -> bool:
        if self._first_part_ip in LIFE_INNER_IPS:
            logging.info(f'_case_LIFE for inner func -> True')
            return True
        return False
