#!/bin/bash
source /root/chatbot/myenv/bin/activate
exec uvicorn app:app --host 0.0.0.0 --port 8888

