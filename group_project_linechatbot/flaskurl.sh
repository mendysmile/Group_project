#!/bin/bash


curl -s "$(docker port flask_ngrok 4040)/api/tunnels" | awk -F',' '{print $3}' | awk -F'"' '{print $4}' | awk -F'//' '{print $2}'
