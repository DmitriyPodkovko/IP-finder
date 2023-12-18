import logging
import cx_Oracle
from functools import wraps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import connections
from django.shortcuts import redirect, render
from config.handler_settings import (ORACLE_FUNCTIONS,
                                     RESULT_DIRECTORY)
from ipfinder.forms import LoginForm
from log.log import create_log_file


class DBAuthentication:
    def __init__(self) -> None:
        self._cursor = None

    def connect_on(self) -> bool:
        try:
            self._cursor = connections['auth'].cursor()
            logging.info(f'auth connect on')
            return True
        except Exception as e:
            logging.error(f'DB error auth connect on:\n {str(e)}')
            return False

    def connect_off(self) -> None:
        try:
            self._cursor.close()
            logging.info(f'auth connect off')
        except Exception as e:
            logging.error(f'DB error auth connect off:\n {str(e)}')

    def check(self, login_, password_) -> tuple:
        result = tuple()
        try:
            if login_ and password_:
                oracle_proc = ORACLE_FUNCTIONS.get('check_login_proc')
                logging.info(f'{oracle_proc}, {login_}')
                id_ = self._cursor.var(cx_Oracle.NUMBER).var
                is_admin_ = self._cursor.var(cx_Oracle.NUMBER).var
                self._cursor.callproc(oracle_proc, [id_, is_admin_, login_, password_])
                result = (round(id_.getvalue()), round(is_admin_.getvalue()))
                logging.info(f'auth done {result}')
            return result
        except Exception as e:
            logging.error(f'DB error auth check:\n {str(e)}')
            return result


def custom_login_required(login_url=None):
    """
    Decorator for requiring user authentication.
    :param login_url: URL to redirect in case of no authentication
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.session.get('is_authenticated', False):
                return redirect(login_url)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def login_view(request):
    form = LoginForm(request.POST) if request.method == 'POST' else LoginForm()
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        auth = DBAuthentication()
        if auth.connect_on():
            try:
                answer = auth.check(username, password)
                if answer[0] > 0:
                    user, created = User.objects.get_or_create(username=username)
                    logging.info(f'Login user: {user}, created: {created}')
                    if user is not None:
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)
                        request.session['id_'] = answer[0]
                        request.session['is_admin_'] = answer[1]
                        request.session['user_'] = username
                        request.session['is_authenticated'] = True
                        user_directory = f'{RESULT_DIRECTORY}/{user}'
                        user_log = f'{user_directory}/{user}.log'
                        request.session['user_directory'] = user_directory
                        request.session['user_log'] = user_log
                        request.session['errors'] = ''
                        create_log_file(user_directory, user_log)
                        return redirect('index')
                else:
                    logging.info(f'Invalid username or password!')
                    messages.error(request, 'Invalid username or password!')
            finally:
                auth.connect_off()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    try:
        user_ = request.session['user_']
        logout(request)
        logging.info(f'Log out user: {user_}')
        return redirect('login')
    except Exception as e:
        logging.error(f'Log out error:\n {str(e)}')
        return redirect('login')
