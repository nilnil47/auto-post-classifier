#!/bin/bash
echo running script
cd auto_post_classifier && poetry run uvicorn main:app --host 0.0.0.0 --port 80