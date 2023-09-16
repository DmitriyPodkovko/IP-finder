FROM oraclelinux:8 AS oracle-client

RUN  dnf -y install oracle-instantclient-release-el8 && \
     dnf -y install oracle-instantclient-basic oracle-instantclient-devel oracle-instantclient-sqlplus && \
     rm -rf /var/cache/dnf

#ARG release=19
#ARG update=18
#
#RUN  dnf -y install oracle-release-el8 && \
#     dnf -y install oracle-instantclient${release}.${update}-basic oracle-instantclient${release}.${update}-devel oracle-instantclient${release}.${update}-sqlplus && \
#     rm -rf /var/cache/dnf

FROM python:3.11-alpine
LABEL maintainer="PDA"

#RUN apk update && apk upgrade && apk add bash
# Define RUN optional
#SHELL ["/bin/bash", "-c"]

WORKDIR /IP-finder

# Set environment variables
# This prevents Python from writing out *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

COPY . .

# "/bin/bash -c" "pip install --upgrade pip"
#RUN pip install --upgrade pip

#COPY ./IP-finder /IP-finder
#COPY ./requirements.txt /requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

#RUN apk update && apk upgrade && \
#    apk add gcc && apk add musl-dev && apk add libaio && apk add gcompat && \
#    pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt

RUN apk add --update --upgrade --no-cache --virtual .tmp-build-deps \
    gcc musl-dev libaio gcompat && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
#    apk del .tmp-build-deps


#RUN python3 -m pip install -U "Cython<3.0.0" setuptools_rust cffi && \
#    python3 -m pip install --no-build-isolation PyYAML "oracledb==1.2.2"
#    python3 -m pip install --no-build-isolation cx_Oracle-8.3.0.tar.gz
#RUN    python3 -m pip install oracledb

# If need a virtual environment
# https://github.com/LondonAppDeveloper/deploy-django-with-docker-compose/blob/main/Dockerfile
#RUN python -m venv /py && \
#    py/bin/pip install --upgrade pip && \
#    py/bin/pip install --no-cache-dir -r requirements.txt && \
#    adduser --disabled-password --no-create-home app
#ENV PATH="/py/bin:$PATH"
#USER app

# If need a pipenv
#COPY Pipfile Pipfile.lock ./
#RUN pip install -U pipenv
#RUN pipenv install --system

# Copying the Oracle client from the first image
COPY --from=oracle-client /usr/lib/oracle /usr/lib/oracle

ENV LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib
#ENV LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib/${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}

# Uncomment if the tools package is added
#ENV PATH=$PATH:/usr/lib/oracle/21/client64/lib

# Uncomment if the tools package is added
#ENV PATH=$PATH:/usr/lib/oracle/${release}.${update}/client64/bin

CMD ["sqlplus", "-v"]

EXPOSE 8247

ENTRYPOINT ["sh", "entrypoint.sh"]
