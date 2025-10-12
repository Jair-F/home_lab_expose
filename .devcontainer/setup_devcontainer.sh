#!/bin/sh

apt install -y apache2
/etc/init.d/apache2 start

git config --global --add safe.directory .
git config --global user.name Jair
git config --global user.email jair.fehlauer@gmail.com

pre-commit install
pre-commit run
