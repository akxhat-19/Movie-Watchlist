FROM python:3.14

WORKDIR /code

COPY requirements.txt /code/requirements.txt

ADD app.py .
ADD tmdb.py .
COPY templates /code/templates
COPY static /code/static
COPY admin /code/admin
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python" , "app.py" , "--host" , "0.0.0.0" ,"--port", "5000"]

