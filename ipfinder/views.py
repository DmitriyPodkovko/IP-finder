import os
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from db.executor import DBExecutor
from excel.handler import ExcelHandler
from .forms import FileFieldForm
from config.settings import (DEBUG, DATABASES,
                             ALLOWED_HOSTS)
from config.handler_settings import (RESULT_DIRECTORY,
                                     ROWS_QUANTITY,
                                     SETTINGS_FILE_PATH)


def create_log_file():
    if not os.path.exists(f'{RESULT_DIRECTORY}/ipfinder.log'):
        logging.basicConfig(filename=f'{RESULT_DIRECTORY}/ipfinder.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            force=True)


if not os.path.exists(RESULT_DIRECTORY):
    os.makedirs(RESULT_DIRECTORY)
create_log_file()
logging.info(f'DEBUG = {DEBUG}')
# logging.info(f'SETTINGS_FILE_PATH = {SETTINGS_FILE_PATH}')
# logging.info(f'STATICFILES_DIRS = {STATICFILES_DIRS}')
# logging.info(f'STATIC_ROOT = {STATIC_ROOT}')
logging.info(f"DATABASES = {DATABASES.get('filter')}")
# logging.info(f'STATIC_URL = {STATIC_URL}')
logging.info(f'ALLOWED_HOSTS = {ALLOWED_HOSTS}')
is_task_cancelled = False


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = 'index.html'
    # success_url = reverse_lazy('loaded')
    success_url = reverse_lazy('index')
    all_warning_numbers = set()

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        global is_task_cancelled
        try:
            create_log_file()
            current_rows_quantity = ROWS_QUANTITY
            files = form.cleaned_data["file_field"]
            # logging.info(f'{self.request.META}')
            logging.info(files)
            for f in files:  # Do with each file.
                logging.info(f'GET: {f}')
                if is_task_cancelled:
                    logging.info("TASK CANCELLED !!!")
                    break
                excel_handler = ExcelHandler(f)
                ip_list = excel_handler.get_ip_list_from_xlsx_file()
                excel_handler.create_output_xlsx_file()
                db_executor = DBExecutor()
                if db_executor.connect_on():
                    try:
                        DST_numbers_ls = []
                        for i, tuple_values in enumerate(ip_list):
                            if is_task_cancelled:
                                logging.info("TASK CANCELLED !!!")
                                break
                            DST_numbers = db_executor.execute(tuple_values)
                            logging.info(f'response: {DST_numbers}')
                            DST_numbers_ls.append(DST_numbers)
                            if DST_numbers:
                                warning_numbers = db_executor.execute_check_numbers(DST_numbers)
                                if warning_numbers:
                                    FileFieldFormView.all_warning_numbers |= warning_numbers
                                    logging.info(f'!!! WARNING NUMBERS: {warning_numbers} !!!')
                            if i + 1 == current_rows_quantity or i + 1 == len(ip_list):
                                excel_handler.save_result_to_output_xlsx_file(DST_numbers_ls)
                                DST_numbers_ls = []
                                current_rows_quantity += ROWS_QUANTITY
                    finally:
                        db_executor.connect_off()

        finally:
            is_task_cancelled = False
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if FileFieldFormView.all_warning_numbers:
            context['warning_numbers'] = FileFieldFormView.all_warning_numbers
            FileFieldFormView.all_warning_numbers = set()
        return context


# class FileLoadedView(TemplateView):
#     template_name = 'loaded.html'

class FileResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_files'] = os.listdir(RESULT_DIRECTORY)
        return context


class CancelTaskView(View):
    def post(self, request, *args, **kwargs):
        global is_task_cancelled
        logging.info("TASK CANCELLATION REQUESTED ...")
        is_task_cancelled = True
        return JsonResponse({"status": "cancelled"})


def delete_file(request):
    if request.method == 'POST':
        # Get the file name from the POST request
        file_name = request.POST.get('file_name')
        file_path = os.path.join(RESULT_DIRECTORY, file_name)
        try:
            # Try to delete the file
            os.remove(file_path)
            response_data = {'success': True}
        except OSError:
            response_data = {'success': False}
        return JsonResponse(response_data)
    # If the request method is not POST, we will return an error
    return JsonResponse({'success': False})


def edit_settings(request):
    if request.method == 'POST':
        new_settings_text = request.POST.get('settings_text', '')
        # Saving new settings in a settings file
        with open(SETTINGS_FILE_PATH, 'w') as file:
            file.write(new_settings_text)
        return JsonResponse({'status': 'success'})
    # Display current settings
    with open(SETTINGS_FILE_PATH, 'r') as file:
        current_settings_text = file.read()
    return render(request, 'edit_settings.html', {'current_settings_text': current_settings_text})
