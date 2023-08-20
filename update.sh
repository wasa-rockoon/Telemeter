#!/usr/bin/env bash

git stash -u
git pull
git stash apply
docker-compose up -d --build
