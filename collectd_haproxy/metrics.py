

# a metric cross reference:
#  <haproxy metric>: (<collectd type instance>, <collectd type>)
METRIC_XREF = {
    # metrics from the "show info" command
    'Nbproc': ('num_processes', 'gauge'),
    'Process_num': ('process_num', 'gauge'),
    'Pid': ('pid', 'gauge'),
    'Uptime_sec': ('uptime_seconds', 'gauge'),
    'Memmax_MB': ('max_memory_mb', 'gauge'),
    'Maxsock': ('max_sockets', 'gauge'),
    'Maxconn': ('max_connections', 'gauge'),
    "Hard_maxconn": ("hard_max_connections", "gauge"),
    'CurrConns': ('current_connections', 'gauge'),
    "CumConns": ("connection_count", "counter"),
    "CumReq": ("request_count", "counter"),
    "MaxSslConns": ("max_ssl_connections", "gauge"),
    "CurrSslConns": ("current_ssl_conenctions", "gauge"),
    "CumSslConns": ("ssl_connection_count", "counter"),
    'Maxpipes': ('max_pipes', 'gauge'),
    'PipesUsed': ('pipes_used', 'gauge'),
    'PipesFree': ('pipes_free', 'gauge'),
    "ConnRate": ("connection_rate", "gauge"),
    "ConnRateLimit": ("max_connection_rate", "gauge"),
    'MaxConnRate': ('peak_connection_rate', 'gauge'),
    "SessRate": ("session_rate", "gauge"),
    "SessRateLimit": ("max_session_rate", "gauge"),
    'MaxSessRate': ('peak_session_rate', 'gauge'),
    "SslRate": ("ssl_rate", "gauge"),
    "SslRateLimit": ("max_ssl_rate", "gauge"),
    "MaxSslRate": ("peak_ssl_rate", "gauge"),
    "SslFrontendKeyRate": ("ssl_frontend_key_rate", "gauge"),
    "SslFrontendMaxKeyRate": ("peak_ssl_frontend_key_rate", "gauge"),
    "SslFrontendSessionReuse_pct": ("ssl_frontend_sess_reuse_pct", "gauge"),
    "SslBackendKeyRate": ("ssl_backend_key_rate", "gauge"),
    "SslBackendMaxKeyRate": ("peak_ssl_backend_key_rate", "gauge"),
    "SslCacheLookups": ("ssl_cache_lookup_count", "counter"),
    "SslCacheMisses": ("ssl_cache_miss_count", "counter"),
    "CompressBpsIn": ("compress_bps_in", "gauge"),
    "CompressBpsOut": ("compress_bps_out", "gauge"),
    "CompressBpsRateLim": ("max_compress_bps_rate", "gauge"),
    "ZlibMemUsage": ("zlib_mem_usage", "gauge"),
    "MaxZlibMemUsage": ("peak_zlib_mem_usage", "gauge"),
    'Tasks': ('tasks', 'gauge'),
    'Run_queue': ('run_queue', 'gauge'),
    "Idle_pct": ("idle_pct", "gauge"),

    # metrics from the "show stat" command
    # see http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.1
    'qcur': ('queued_request_count', 'gauge'),
    "qmax": ("peak_queued_request_count", "gauge"),
    'scur': ('current_session_count', 'gauge'),
    "smax": ("peak_session_count", "gauge"),
    "slim": ("max_sessions", "gauge"),
    'stot': ('session_count', 'counter'),
    'bin': ('bytes_in', 'gauge'),
    'bout': ('bytes_out', 'gauge'),
    'dreq': ('denied_request_count', 'counter'),
    'dresp': ('denied_response_count', 'counter'),
    'ereq': ('error_request_count', 'counter'),
    'econ': ('error_connection_count', 'counter'),
    'eresp': ('error_response_count', 'counter'),
    'wretr': ('conn_retry_count', 'counter'),
    'wredis': ('redispatch_count', 'counter'),
    "status": ("status", "gauge"),
    "weight": ("server_weight", "gauge"),
    "act": ("active_server_count", "gauge"),
    "bck": ("backup_server_count", "gauge"),
    'chkfail': ('failed_check_count', 'counter'),
    "chkdown": ("down_transition_count", "counter"),
    "lastchg": ("last_change_seconds", "counter"),
    'downtime': ('downtime_seconds', 'counter'),
    "qlimit": ("max_queue", "gauge"),
    "throttle": ("throttle_pct", "gauge"),
    "lbtot": ("selection_count", "counter"),
    'rate': ('session_rate', 'gauge'),
    "rate_lim": ("max_session_rate", "gauge"),
    "rate_max": ("peak_session_rate", "gauge"),
    "check_duration": ("check_duration", "gauge"),
    'hrsp_1xx': ('http_response_1xx', 'counter'),
    'hrsp_2xx': ('http_response_2xx', 'counter'),
    'hrsp_3xx': ('http_response_3xx', 'counter'),
    'hrsp_4xx': ('http_response_4xx', 'counter'),
    'hrsp_5xx': ('http_response_5xx', 'counter'),
    'hrsp_other': ('http_response_other', 'counter'),
    'req_rate': ('request_rate', 'gauge'),
    "req_rate_max": ("peak_request_rate", "gauge"),
    "req_tot": ("request_count", "counter"),
    "cli_abrt": ("client_abort_count", "counter"),
    "srv_abrt": ("server_abort_count", "counter"),
    "qtime": ("avg_queue_time", "gauge"),
    "ctime": ("avg_connect_time", "gauge"),
    "rtime": ("avg_response_time", "gauge"),
    "ttime": ("avg_total_session_time", "gauge"),
}


TEXT_METRICS = {
    "status": {
        "NOLB": 0,  # server receives conns, is not included in load balancing
        "MAINT": 1,  # server is marked as under maintenance
        "UP": 2,  # server is up
        "DOWN": 3,  # server is down
    },
    "check_status": {
        "UNK": 0,  # unknown
        "INI": 1,  # initializing
        "SOCKERR": 2,  # socket error
        "L4OK": 3,  # layer 4 ok, no upper layers tested,
        "L4TOUT": 4,  # layer 1-4 timeout
        "L4CON": 5,  # layer 1-4 connection problem
        "L6OK": 6,  # check passed on layer 6
        "L6TOUT": 7,  # layer 6 (SSL) timeout
        "L6RSP": 8,  # layer 6 invalid response - protocol error
        "L7OK": 9,  # check passed on layer 7
        "L7OKC": 10,  # check conditionally passed on layer 7
        "L7TOUT": 11,  # layer 7 (HTTP/SMTP) timeout
        "L7RSP": 12,  # layer 7 invalid response - protocol error
        "L7STS": 13,  # layer 7 response error, for example HTTP 5xx
    }
}
