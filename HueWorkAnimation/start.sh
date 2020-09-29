docker build -t web-server .

docker run -d --restart unless-stopped --name web-server -v$PWD/model:/web-server -p 192.168.178.50:1337:1337 web-server

