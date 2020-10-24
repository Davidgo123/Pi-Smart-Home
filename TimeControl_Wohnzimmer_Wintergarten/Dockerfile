#publicly available docker image "python" on docker hub will be pulled
FROM python:3.6

ADD timeControl.py /

# Erweiterungen
RUN pip3 install requests

# Trigger Python script
CMD ["python", "./timeControl.py"]


