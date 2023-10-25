#!/bin/bash
echo running script
poetry run python auto_post_classifier/main.py -d data/AntiIsraeli.csv --no-shuffle --no-api -n -1
