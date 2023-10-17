import logging


def exceptor_():
    msg = """This exception occurred due to 
    the fact that the file was not passed as 
    an argument to the constructor of the ExcelHandler 
    class (ipfinder.views.py) or was not passed as 
    an argument to the 
    method get_ip_list_from_xlsx_file (ipfinder.api.file_).
    """
    try:
        exit(666)
    except Exception as err:
        logging.info(err)
        logging.info(msg=msg)
