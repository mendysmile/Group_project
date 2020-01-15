#!/bin/bash
docker-compose up -d
declare -x TOKEN=NSyoANWBvLGIQZx71vqHv5+Ks4sO+dRlXXumIkStNac9t2b5aURmXqCT+A7CTzBqCBvp0CEhYJ//etFjFk3AVPbrnsGjZpF/nuOxVhcDdZ1A1tHNrkHwbZ4P9EbrO4EDwtjbnerrTUveOrJUNdDIFQdB04t89/1O/w1cDnyilFU=
declare -x SKEY=30c12f820ce59b11a3289eabae18cc9f
declare -x SELFUID=Ube5917bf2a3bb2a058ceb255d186030d
declare -x RICHMID=richmenu-f9e7c3d20c3938352b343402f8cc183a
#執行shell
bash lineurl.sh
bash flaskurl.sh
#取消環境變數
unset TOKEN
unset SKEY
unset SELFUID
unset RICHMID

