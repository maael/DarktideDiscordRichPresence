@echo off

for %%A in ("%~dp0\server\discord-presence-server.exe") do set "SERVER_EXE=%%~fA"

echo "[INFO] Starting server exe from server_exe:%SERVER_EXE%" >> server.log

start "" "%SERVER_EXE%"

echo [INFO] Server exe launched async >> server.log
