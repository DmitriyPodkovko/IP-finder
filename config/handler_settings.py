from config.settings import BASE_DIR

# Excel result column name
DESTINATION_NUMBER = 'DST number'

# Quantity of rows per portion to save in xlsx output file
ROWS_QUANTITY = 100

# output filename = input filename + prefix
# for example:
# test_result.xlsx = test.xlsx + _result
EXCEL_OUTPUT_FILE_PREFIX = '_result'

# Build paths like this: BASE_DIR / 'subdir'
# BASE_DIR - on the server
RESULT_DIRECTORY = BASE_DIR / 'result'

SETTINGS_FILE_PATH = str(BASE_DIR / 'config' / 'handler_settings.py')

# Excel columns and rows settings for extracting values
# Column numbering starts from 0
# Row numbering starts from 1
# If DST column < 0 then a new column called
# DESTINATION_NUMBER will be created
EXCEL_ROW_COLUMN = {
    'default': {
        'Start_row': 2,
        'IP_DST': 4,
        'Port_DST': 5,
        'Date': 6,
        'Time': 7,
        'Provider': 8,
        'DST': 10,
    }
}

OPERATORS = {
    '3Mob': '3MOB',
    'Vodafone': 'MTS',
    'UMC': 'MTS',
    'MTS': 'MTS',
    'VF-Ukraine': 'MTS',
    'VF UKRAINE': 'MTS',
    'KS': 'KS',
    'Kyivstar': 'KS',
    'Kyivstar UA': 'KS',
    'Kievstar': 'KS',
    'Kievstar GSM': 'KS',
    'lifecell': 'LIFE',
    'Lifecell': 'LIFE',
    'LifeCell': 'LIFE',
    'life': 'LIFE',
    'LIFE': 'LIFE',
    'LIFECELL': 'LIFE',
    'life:)': 'LIFE'
}

MOB3_IPS = ()
MTS_IPS = ('46.133', '89.209', '31.144', '128.124', '178.133')
KS_IPS = ('46.211', '94.153.112')
LIFE_IPS = ('37.73', '46.96', '88.154', '88.155')

# MOB3_INNER_IPS = (10, 37, 192)
# MTS_INNER_IPS = (10, 11, 100, 192)
# KS_INNER_IPS = (10, 11, 100, 111, 134, 188, 192, '2a02')
# LIFE_INNER_IPS = (10, 11, 100, 192)

ORACLE_FUNCTIONS = {
    # 'tel_func': 'NEVA.ip_tr.restore_tel_from_ip_list',
    'tel_func': 'NEVA.ip_tr.get_ip_list',
    # 'inner_tel_func': 'NEVA.ip_tr.restore_tel_from_inner_ip_list',
    'inner_tel_func': 'NEVA.ip_tr.get_inner_ip_list',
    'check_tel_func': 'NEVA.ip_tr.check_tel',
    'check_login_proc': 'check_login'
}
