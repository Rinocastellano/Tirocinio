FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 1026
ENV FLASK_APP=dockers.py
CMD [ "python3" , "tutorial.py"]
CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]
