FROM python:3.7-slim
COPY ./ /app
RUN pip install -r /app/requirements.txt
WORKDIR /app/foodgram/
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]