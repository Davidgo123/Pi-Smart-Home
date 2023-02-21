docker build -t heizungssteuerung .

docker run -d --restart unless-stopped --name heizungssteuerung heizungssteuerung
