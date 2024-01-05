#!/bin/bash
echo running script
poetry run uvicorn main:app --host 0.0.0.0 --port 80