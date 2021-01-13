@set /A PORT = 8888
start python -m scripts.main_server local %PORT% 0 1&
start python -m scripts.main_client local %PORT%&
start python -m scripts.main_client local %PORT%