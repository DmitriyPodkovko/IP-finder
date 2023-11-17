import os
import logging
from functools import wraps
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from db.executor import DBExecutor
from excel.handler import ExcelHandler
from .forms import FileFieldForm, LoginForm
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
processed_rows: int = 0
total_xlsx_rows: int = 0
current_file_index: int = 0
next_file_index: bool = False
authenticated: bool = False


def custom_login_required(login_url=None):
    """
    Decorator for requiring user authentication.
    :param login_url: URL to redirect in case of no authentication
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # if not request.user.is_authenticated:
            if not authenticated:
                return redirect(login_url)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator


# @method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(custom_login_required(login_url='login'), name='dispatch')
class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = 'index.html'
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
        global is_task_cancelled, current_file_index, next_file_index
        global processed_rows, total_xlsx_rows
        try:
            create_log_file()
            current_rows_quantity = ROWS_QUANTITY
            files = form.cleaned_data["file_field"]
            # logging.info(f'{self.request.META}')
            logging.info(files)
            for k, f in enumerate(files):  # Do with each file.
                current_file_index = k
                logging.info(f'GET: {f}')
                if is_task_cancelled:
                    logging.info("TASK CANCELLED !!!")
                    break
                excel_handler = ExcelHandler(f)
                ip_list = excel_handler.get_ip_list_from_xlsx_file()
                total_xlsx_rows = len(ip_list)
                excel_handler.create_output_xlsx_file()
                db_executor = DBExecutor()
                if db_executor.connect_on():
                    try:
                        DST_numbers_ls = []
                        processed_rows = 0
                        for i, tuple_values in enumerate(ip_list):
                            if is_task_cancelled:
                                logging.info("TASK CANCELLED !!!")
                                break
                            DST_numbers = db_executor.execute(tuple_values)
                            logging.info(f'response: {DST_numbers}')
                            # if response is error then repeat request 5 time
                            if DST_numbers and next(iter(DST_numbers)) == 'ERROR':
                                for j in range(5):
                                    DST_numbers = db_executor.execute(tuple_values)
                                    if DST_numbers and next(iter(DST_numbers)) != 'ERROR':
                                        break
                            DST_numbers_ls.append(DST_numbers)
                            if DST_numbers and next(iter(DST_numbers)) != 'ERROR':
                                warning_numbers = db_executor.execute_check_numbers(DST_numbers)
                                if warning_numbers:
                                    FileFieldFormView.all_warning_numbers |= warning_numbers
                                    logging.info(f'!!! WARNING NUMBERS: {warning_numbers} !!!')
                            if i + 1 == current_rows_quantity or i + 1 == len(ip_list):
                                excel_handler.save_result_to_output_xlsx_file(DST_numbers_ls)
                                DST_numbers_ls = []
                                current_rows_quantity += ROWS_QUANTITY
                            processed_rows += 1
                    finally:
                        next_file_index = True
                        processed_rows = 0
                        db_executor.connect_off()
        finally:
            current_file_index = 0
            next_file_index = False
            is_task_cancelled = False
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if FileFieldFormView.all_warning_numbers:
            context['warning_numbers'] = FileFieldFormView.all_warning_numbers
            FileFieldFormView.all_warning_numbers = set()
        return context

    # @method_decorator(custom_login_required(login_url='login'))
    # def dispatch(self, *args, **kwargs):
    #     if not self.request.session.get('is_authenticated', False):
    #     if not is_authenticated:
    #         return HttpResponseRedirect('login')
    #     return super().dispatch(*args, **kwargs)


# class FileLoadedView(TemplateView):
#     template_name = 'loaded.html'

@method_decorator(custom_login_required(login_url='login'), name='dispatch')
class FileResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_files'] = os.listdir(RESULT_DIRECTORY)
        return context


@method_decorator(custom_login_required(login_url='login'), name='dispatch')
class CancelTaskView(View):
    def post(self, request, *args, **kwargs):
        global is_task_cancelled
        logging.info("TASK CANCELLATION REQUESTED ...")
        is_task_cancelled = True
        return JsonResponse({"status": "cancelled"})


@custom_login_required(login_url='login')
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


@custom_login_required(login_url='login')
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
    return render(request, 'edit_settings.html',
                  {'current_settings_text': current_settings_text})


def check_processing_status(request):
    global current_file_index, next_file_index
    file_index = current_file_index
    if total_xlsx_rows == 0:
        progress_percent = 0
    else:
        progress_percent = round((processed_rows / total_xlsx_rows) * 100)
    if next_file_index:
        progress_percent = 100
        file_index -= 1
        next_file_index = False
    return JsonResponse({'progress': progress_percent,
                         'file_index': file_index})


# class LoginFormView(TemplateView):
#     form_class = LoginForm
#     template_name = 'login.html'

def login_view(request):
    global authenticated
    form = LoginForm(request.POST) if request.method == 'POST' else LoginForm()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # call procedure
        # user = authenticate(request, username=username, password=password)
        user = username
        # user = None
        logging.info(f'User: {user}')
        if user is not None:
            # login(request, user)
            # request.session['is_authenticated'] = True
            authenticated = True
            user_directory = f'{RESULT_DIRECTORY}/{user}'
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            return redirect('index')
        else:
            logging.info(f'Invalid username or password')
            # messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {'form': form})
