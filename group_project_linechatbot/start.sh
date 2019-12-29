#!/bin/bash
docker-compose up -d
declare -x TOKEN=PkNfpRA24L2bkIcr0ScCTctkPUCje+oUCUPHyAQ3r/rLXOmZ+FEMAkEzYEz1yTpmW+RnCW4zIAyK2mz1B6j8pg/FDYjR+hS3Fa41yxVIt5o3XwRUEdT598gIq8T6afW7OwQLVkIWiIV8+4k+28qna1GUYhWQfeY8sLGRXgo3xvw=
declare -x SKEY=fe450ff38eb58b843847f6656839144c
declare -x SELFUID=Ube5917bf2a3bb2a058ceb255d186030d
declare -x RICHMID=richmenu-e6f2e2139c8cfaf500ac2e1b73580174
#執行shell
bash lineurl.sh
bash flaskurl.sh
#取消環境變數
unset TOKEN
unset SKEY
unset SELFUID
unset RICHMID

