@set /A PORT = 8888
start python -m scripts.main_server local %PORT% 0 0&
ping 127.0.0.1 -n 5 > nul
start python -m scripts.main_client local %PORT%&
start python -m scripts.main_client local %PORT%