FROM python:3.6

ADD Heizungssteuerung.py /
ENV TZ=Europe/Berlin

# Erweiterungen
RUN pip3 install requests
RUN pip3 install fritzconnection

# Trigger Python script
CMD ["python","-u","./Heizungssteuerung.py"]