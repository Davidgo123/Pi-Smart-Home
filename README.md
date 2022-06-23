# Pi-NetworkControl
[Control AV Receiver (RX 475) Volume] 

- Auto reset AV Receiver Volume to -30db by switch from Spotify to PC Input
- Auto reset AV Receiver Volume to -50db by switch from PC to Spotify Input
- Set Volume via HTTP 

[Control Hue Lamps over Webserver]

- Work Skript (60min cold white, then 5 min warm white)
  - When aktivate again -> Full time warm white
  - Arrival with HTTP Get (192.168.178.50:1337/work)
- Cozy (dark orange on all Lamps)
  - Arrival with HTTP Get (192.168.178.50:1337/cozy)
