@echo off

for %%A in ("%~dp0\server\discord-presence-server.exe") do set "SERVER_EXE=%%~fA"

start "" "%SERVER_EXE%"
