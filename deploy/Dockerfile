FROM katalonstudio/python:latest

ARG workdir=/workspace
WORKDIR $workdir
RUN chmod -R a+w /workspace

EXPOSE 8000

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt -y install build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN rm requirements.txt

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
