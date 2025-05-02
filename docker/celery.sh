#!/bin/bash

cd src

celery --app=tasks.tasks:celery worker -l INFO
