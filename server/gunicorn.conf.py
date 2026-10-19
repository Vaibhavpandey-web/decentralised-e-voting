import os

bind = '0.0.0.0:' + os.getenv('PORT', '10000')
# One process keeps the default in-memory limiter consistent. Use external
# RATE_LIMIT_STORAGE before scaling workers or replicas.
workers = 1
threads = 2
timeout = 120
accesslog = '-'
errorlog = '-'
# Do not trust client-supplied forwarding headers by default.
forwarded_allow_ips = os.getenv('FORWARDED_ALLOW_IPS', '127.0.0.1')
