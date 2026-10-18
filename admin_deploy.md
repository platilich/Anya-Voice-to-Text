# Admin Deploy

Quick tunnel with HTTPS

This file shows a fast way to open your Django Admin panel with HTTPS using Cloudflare Tunnel (cloudflared). This is free and easy. It gives a public HTTPS URL like https://xxxxx.trycloudflare.com

Prerequisites

- Your Django admin runs on the server at 127.0.0.1:8000 (gunicorn or runserver).
- SSH access to the server.
- sudo rights.

Install cloudflared

For Raspberry Pi 5 (arm64):

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -O cloudflared.deb
sudo dpkg -i cloudflared.deb
```

For amd64 Linux:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -O cloudflared.deb
sudo dpkg -i cloudflared.deb
```

Quick tunnel (free and easy)

1. Start your Django admin on localhost (example with runserver or gunicorn):

```bash
# simple test (not for production)
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000

# or run gunicorn (replace myproject with your project name)
# venv/bin/gunicorn myproject.wsgi:application -b 127.0.0.1:8000 --workers 2
```

2. Start cloudflared tunnel to the local port:

```bash
sudo cloudflared tunnel --url http://127.0.0.1:8000
```

3. In the output you will see a public URL like:

```
https://xxxxxx.trycloudflare.com
```

Open this URL in your browser. It is HTTPS and it leads to your Django admin.

Run cloudflared as a service (optional)

To keep the tunnel running, make a systemd service for cloudflared.

Create file /etc/systemd/system/cloudflared.service and add:

```ini
[Unit]
Description=Cloudflared Tunnel
After=network.target

[Service]
Type=simple
User=your_username
ExecStart=/usr/local/bin/cloudflared tunnel --url http://127.0.0.1:8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `your_username` with your server user. If cloudflared is at /usr/bin/cloudflared, use that path.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

Security notes

- Use DEBUG=False in production.
- Keep SECRET_KEY and other secrets out of the code (use .env).
- The trycloudflare URL is public. Use it only for trusted users or testing.
- For more security, consider Cloudflare Access (Zero Trust) or use a Cloudflare account and a custom domain.

Done

This file gives a quick and free way to open your Django Admin with HTTPS using cloudflared.
