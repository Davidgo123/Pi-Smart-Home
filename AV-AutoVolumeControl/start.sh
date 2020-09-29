docker build -t av-spotify-volume .

docker run -d --restart unless-stopped av-spotify-volume
