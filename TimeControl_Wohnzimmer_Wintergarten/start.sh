docker build -t timecontrol .

docker run -d --restart unless-stopped --name timecontrol timecontrol
