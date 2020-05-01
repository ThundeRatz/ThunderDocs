#!/bin/bash

sudo cp ./config/*.nginx /etc/nginx/sites-available
sudo cp ./config/*.service /etc/systemd/system/

sudo nginx -s reload

systemctl daemon-reload
sudo systemctl restart trdocs
