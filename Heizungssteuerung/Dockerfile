FROM python

# ArbeitsOrdner
WORKDIR /

# Erweiterungen
RUN pip3 install requests
RUN pip3 install FritzHosts

COPY . /
ENTRYPOINT ["python3"]

# Ausfuehren des Skripts
CMD ["Heizungssteuerung.py"]
