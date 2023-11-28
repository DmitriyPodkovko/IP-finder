import os
import logging


def create_log_file(user_directory, user_log):
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    logging.basicConfig(filename=f'{user_log}',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        force=True)
