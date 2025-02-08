# gunicorn_config.py
timeout = 300  # 增加到 300 秒（5 分钟）
workers = 2  # 增加 Worker 进程，防止单个请求卡住整个应用
