import logging
import os
from django.http import JsonResponse

from django.views.generic.edit import FormView
from django.views.generic import TemplateView

import config.settings
from db.executor import DBExecutor
from excel.handler import ExcelHandler
from .forms import FileFieldForm
from django.urls import reverse_lazy

logging.basicConfig(filename='ipfinder.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f'DEBUG = {config.settings.DEBUG}')
logging.info(f'STATICFILES_DIRS = {config.settings.STATICFILES_DIRS}')
# logging.info(f'STATIC_ROOT = {config.settings.STATIC_ROOT}')
logging.info(f"DATABASES = {config.settings.DATABASES.get('filter')}")
logging.info(f'SECRET_KEY = {config.settings.SECRET_KEY}')
logging.info(f'STATIC_URL = {config.settings.STATIC_URL}')
logging.info(f'ALLOWED_HOSTS = {config.settings.ALLOWED_HOSTS}')

# def index(request):
#     print('qwerty')
#     return render(request, 'index.html')


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = 'index.html'
    # success_url = reverse_lazy('loaded')
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        # logging.info('111111111111')
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # logging.info('222222222222')
        if form.is_valid():
            # logging.info('33333333333')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        logging.info(f'{self.request}')
        logging.info(f'{self.request.path}')
        logging.info(f'{self.request.path_info}')
        logging.info(f'{self.request.META}')
        logging.info(files)
        for f in files:  # Do with each file.
            # logging.info('55555555555')
            logging.info(f'{f}')
            # logging.info(f'{f.path}')
            excel_handler = ExcelHandler(f)
            ip_list = excel_handler.get_ip_list_from_xlsx_file()
            excel_handler.create_output_xlsx_file()
            # logging.info(f'IP_DST, Port_DST, Date, Time, Provider: {ip_list}')
            db_executor = DBExecutor()
            if db_executor.connect_on():
                for i in ip_list:
                    DST_set = db_executor.execute(i)
                    logging.info(f'DST_set from views: {DST_set}')
                    excel_handler.save_result_to_output_xlsx_file(DST_set)
                    db_executor.connect_off()
                    db_executor.connect_on()
                db_executor.connect_off()
        return super().form_valid(form)


# class FileLoadedView(TemplateView):
#     template_name = 'loaded.html'

class FileResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_files'] = os.listdir(config.settings.RESULT_DIRECTORY)
        return context


def delete_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')  # Получаем имя файла из POST-запроса
        file_path = os.path.join(config.settings.RESULT_DIRECTORY, file_name)
        try:
            # Попытаемся удалить файл
            os.remove(file_path)
            response_data = {'success': True}
        except OSError:
            response_data = {'success': False}
        return JsonResponse(response_data)
    # Если метод запроса не POST, вернем ошибку
    return JsonResponse({'success': False})
