docker build -t av-spotify-volume .

docker run -d --restart unless-stopped --name av-spotify-volume av-spotify-volume
