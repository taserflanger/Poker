#!/bin/bash
port=8888
python -m scripts.main_server local $port 0 1 &
python -m scripts.main_client local $port &
python -m scripts.main_client local $port &