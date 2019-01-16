from python:alpine

RUN apk add --no-cache git postgresql-dev gcc libc-dev gettext
RUN apk add --no-cache gcc g++ make libffi-dev python3-dev build-base jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

RUN pip install gunicorn
RUN pip install psycopg2
RUN pip install ipdb
RUN pip install ipython

WORKDIR /app

RUN git clone https://github.com/decide-ganimedes/decide-ganimedes.git .
ADD ./authentication/migrations ./decide/authentication/migrations
ADD ./base/migrations ./decide/base/migrations
ADD ./census/migrations ./decide/census/migrations
ADD ./mixnet/migrations ./decide/mixnet/migrations
ADD ./store/migrations ./decide/store/migrations
ADD ./voting/migrations ./decide/voting/migrations
RUN pip install -r requirements.txt

WORKDIR /app/decide
ADD docker-settings.py /app/decide/local_settings.py
RUN ./manage.py collectstatic
RUN ./manage.py compilemessages

