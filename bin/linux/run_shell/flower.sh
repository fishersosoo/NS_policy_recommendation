#!/bin/bash
nohup celery flower --address=0.0.0.0 --port=9999 --broker=amqp://guest:guest@127.0.0.1:8001// --url-prefix=flower > /dev/null 2>&1 &
exit 0

