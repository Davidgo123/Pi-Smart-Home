docker build -t timecontrol .

docker run -d --restart unless-stopped timecontrol
