# Putting the website online

`start-site.py` runs Flask's development server, which is not meant for the
public.  On a server, run the website with [gunicorn](https://gunicorn.org)
(installed by `requirements.txt`) behind a web server such as nginx, which
handles HTTPS.

## The website

On the server, set up the checkout, Sage, the dependencies and the database
as on your computer ([SETUP_POSTGRES.md](SETUP_POSTGRES.md)), with real
passwords.  Then, from the root of the checkout:

```
sage -python -m gunicorn --workers 4 --bind 127.0.0.1:8000 --timeout 60 website.app:app
```

Do not run it in debug mode (`--debug` of `start-site.py`): debug mode shows
errors, with code, to anyone.

To keep it running and start it with the machine, use systemd, with a file
`/etc/systemd/system/mysite.service`:

```ini
[Unit]
Description=mysite website
After=network.target postgresql.service

[Service]
User=mysite
WorkingDirectory=/home/mysite/mysite
ExecStart=/path/to/sage -python -m gunicorn --workers 4 --bind 127.0.0.1:8000 --timeout 60 website.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

then `sudo systemctl enable --now mysite`.  After updating the code
(`git pull`, `sage -pip install -r requirements.txt`), restart it:
`sudo systemctl restart mysite`.

## nginx

A server block passing requests to gunicorn (with HTTPS from
[certbot](https://certbot.eff.org)):

```nginx
server {
    server_name mysite.example.org;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
}
```

The website trusts these headers (see `ProxyFix` in `website/app.py`) to know
its own address.

## Editing knowls: beta and production

Like the LMFDB, a website can run in two copies on the same database:

- a *beta* website, where editors log in and edit knowls, and which shows
  knowls awaiting review: run it with the environment variable that makes
  `Site.is_beta()` true (by default, debug mode; override `is_beta` in
  `website/site.py` to use, say, `os.environ.get("BETA") == "1"` instead);
- the public website, which shows the last reviewed version of each knowl,
  connecting with a read-only role (see "A public read-only copy" in
  [SETUP_POSTGRES.md](SETUP_POSTGRES.md)) so that nobody can log in there.

A small website can also run a single copy, where editors log in directly.

## Checklist

- `secret_key` (next to `config.ini`) is created on first run: keep it, or
  everyone is logged out when it changes.
- `config.ini`, `secrets.ini` and `secret_key` are readable only by the user
  running the website.
- Backups of the database (`pg_dump`, see [SETUP_POSTGRES.md](SETUP_POSTGRES.md)).
- `/health` answers `OK` while the website and its database work: point your
  monitoring at it.
- Logs: gunicorn's (in the systemd journal: `journalctl -u mysite`), and slow
  searches in `logs/slow_queries.log`.
