FROM python

# ArbeitsOrdner
WORKDIR /

# Erweiterungen
RUN pip3 install requests
RUN pip3 install flask

COPY . /
ENTRYPOINT ["python3"]

# Ausfuehren des Skripts
CMD ["model/WebServer.py"]
