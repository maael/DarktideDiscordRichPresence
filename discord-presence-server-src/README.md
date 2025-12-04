# Python Discord RPC HTTP Server (No Flask)

## Install dependencies

```
pip install -r requirements.txt
```

## Build single-file EXE

```sh
pyinstaller --onefile discord-presence-server.py --add-data "config.json;." --noconsole
```

> [!WARNING]
> Seems like `pyinstaller --onefile` triggers on VirusTotal.

### Nuitka

Install Nuitka with:

```sh
python -m pip install -U Nuitka
```

then bundle the exe with:

```sh
nuitka discord-presence-server.py --mode=standalone --include-data-file=config.json=./config.json --windows-console-mode=attach --file-version=1.0.0 --windows-icon-from-ico=../assets/app_icon.ico
```

This will generate a `discord-presence-server.dist` with the `exe` and other needed files in `discord-presence-server-src`.

## Testing

```sh
curl http://127.0.0.1:3923/health
```

```sh
curl -Method POST `
     -ContentType "application/json" `
     -Body '{"state":"Testing RPC","details":"Sent from PowerShell","large_image":"large","large_text":"Hover text"}' `
     http://127.0.0.1:3923/presence/set
```

```sh
curl -Method POST http://127.0.0.1:3923/presence/clear
```

## Notes

- Hosts a simple http server to allow publishing to Discord Rich Presence via Pypresence
- Watches for `Darktide.exe` to know when to exit

## Known issues

- Terminal window opens, likely when server is handling request
