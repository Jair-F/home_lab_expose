#!/bin/sh

apk add git bash fish

git config --global --add safe.directory .
git config --global user.name Jair
git config --global user.email jair.fehlauer@gmail.com

pre-commit install
pre-commit run
