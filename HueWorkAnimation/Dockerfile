FROM python

WORKDIR /


# Erweiterungen
RUN pip3 install requests
RUN pip3 install flask


COPY . /


ENTRYPOINT ["python3"]

CMD ["model/WebServer.py"]
