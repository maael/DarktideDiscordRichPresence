# Python Discord RPC HTTP Server (No Flask)

## Install dependencies

```
pip install -r requirements.txt
```

## Build single-file EXE

```
pyinstaller --onefile discord-presence-server.py --add-data "config.json;." --noconsole
```

## Testing

```
curl http://127.0.0.1:3923/health
```

```
curl -Method POST `
     -ContentType "application/json" `
     -Body '{"state":"Testing RPC","details":"Sent from PowerShell","large_image":"large","large_text":"Hover text"}' `
     http://127.0.0.1:3923/presence/set
```

```
curl -Method POST http://127.0.0.1:3923/presence/clear
```

## Notes

- Hosts a simple http server to allow publishing to Discord Rich Presence via Pypresence
- Watches for `Darktide.exe` to know when to exit

## Known issues

- Terminal window opens, likely when server is handling request
