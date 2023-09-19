import os
import logging
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from db.executor import DBExecutor
from excel.handler import ExcelHandler
from .forms import FileFieldForm
from config.settings import (RESULT_DIRECTORY,
                             DEBUG, DATABASES,
                             ALLOWED_HOSTS)

logging.basicConfig(filename=f'{RESULT_DIRECTORY}/ipfinder.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f'DEBUG = {DEBUG}')
# logging.info(f'STATICFILES_DIRS = {STATICFILES_DIRS}')
# logging.info(f'STATIC_ROOT = {STATIC_ROOT}')
logging.info(f"DATABASES = {DATABASES.get('filter')}")
# logging.info(f'STATIC_URL = {STATIC_URL}')
logging.info(f'ALLOWED_HOSTS = {ALLOWED_HOSTS}')

# def index(request):
#     print('qwerty')
#     return render(request, 'index.html')


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = 'index.html'
    # success_url = reverse_lazy('loaded')
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        # logging.info(f'{self.request.META}')
        logging.info(files)
        for f in files:  # Do with each file.
            logging.info(f'{f}')
            excel_handler = ExcelHandler(f)
            ip_list = excel_handler.get_ip_list_from_xlsx_file()
            excel_handler.create_output_xlsx_file()
            db_executor = DBExecutor()
            if db_executor.connect_on():
                for i in ip_list:
                    DST_set = db_executor.execute(i)
                    logging.info(f'DST_set from views: {DST_set}')
                    excel_handler.save_result_to_output_xlsx_file(DST_set)
                db_executor.connect_off()
        return super().form_valid(form)


# class FileLoadedView(TemplateView):
#     template_name = 'loaded.html'

class FileResultView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result_files'] = os.listdir(RESULT_DIRECTORY)
        return context


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
