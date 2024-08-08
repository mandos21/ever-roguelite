import multiprocessing

# Bind to port 8000
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True
worker_class = "gthread"
worker_connections = 1000
timeout = 30
keepalive = 2
