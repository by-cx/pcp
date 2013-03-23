# -*- coding: utf-8 -*-.

EMAIL_FROM = "info@rosti.cz"
EMAIL_HOST = "localhost"

DEFAULT_MYSQL_COMMAND = 'mysql -uroot'

CRISPY_TEMPLATE_PACK = 'bootstrap'

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "email": ("info@rosti.cz", "Your e-mail"),

    "mode": ("nginx", "apache or nginx"), # main web server, (apache/nginx)
    "ipv6": (True, "Turn on/off support for IPv6"),
    "maildir": ("/var/mail", "Directory with maildirs"),

    "nginx_conf": ("/etc/nginx/sites-enabled/99_auto.conf", "Nginx's config file"),
    "nginx_init_script": ("/etc/init.d/nginx", "Nginx's init script"),
    "nginx_listen": ("[::]:80", "Listen config directive"),
    "nginx_ssl_listen": ("[::]:443", "Listen config directive"),
    "nginx_log_dir": ("/var/log/webx/", "NGINX log directory"),

    "apache_conf": ("/etc/apache2/vhosts.d/99_auto.conf", "Apache's config file"),
    "apache_url": ("127.0.0.1:8080", "Apache proxy URL (for nginx)"), # for nginx as proxy
    "apache_init_script": ("/etc/init.d/apache2", "Apache's init script"),
    "apache_user": ('www-data', "Apache's user"), # 'apache' in gentoo
    "apache_log_dir": ("/var/log/webs/", "Apache log directory"),
    "fastcgi_wrapper_dir": ("/var/www/%s/php5-wrap", "PATH to fastcgi wrapper (user will be filled)"),

    "uwsgi_conf": ("/etc/uwsgi/config.xml", "uWSGI's XML config file"),
    "uwsgi_pidfile": ("/var/run/uwsgi/app_%d.pid", "uWSGI's app pidfile"),
    "uwsgi_memory": (192, "Memory for uWSGI app"),

    "bind_conf": ("/etc/bind/named.pandora.auto", "BIND's config"),
    "bind_zone_conf": ("/etc/bind/pri_auto/%s.zone", "BIND's zone file"),
    "bind_init_script": ("/etc/init.d/bind9", "BIND's init script"),

    "handle_dns": (False, "Use BIND"),
    "handle_dns_secondary": (False, "If handled DNS, include secondary too?"),
    "dns_master": ("", "Master NS server (IP)"),
    "dns_slave": ("", "Slave NS server (IP)"),
    "dns_ns1": ("ns1.example.com", "NS1 domain"),
    "dns_ns2": ("ns2.example.com", "NS2 domain"),
    "dns_mx": ("mail.example.com", "MX server"),
    "dns_email": ("info.example.com", "Admin of DNS"),
    "dns_refresh": (3600, "Refresh"),
    "dns_retry": (1800, "Retry"),
    "dns_expire": (604800, "Expire"),
    "dns_minimum": (30, "Minimum"),
    "dns_default_a": ("87.236.194.121", "Default A"),
    "dns_default_aaaa": ("2a01:5f0:1022:1::1", "Default AAAA"),
    "dns_default_mx": ("mail.rosti.cz.", "Default MX"),
    "dns_default_nss": ("ns1.rosti.cz ns2.rosti.cz", "Default NS servers separated by spaces. First one is primary/master."),
    "dns_default_nss_ips": ("87.236.194.121 89.111.104.70", "Default NS servers IPs separated by spaces. First one is primary/master."),
    "dns_default_record_ttl": (3600, "Default TTL of records"),
    "bind_master_config_file": ("/etc/bind/config.master.conf", "Path to master bind config file"),
    "bind_slave_config_file": ("/etc/bind/config.slave.conf", "Path to slave bind config file"),
    "bind_master_zones_dir": ("/etc/bind/zones", "Path to slave bind zones directory"),
    "bind_slave_zones_dir": ("/etc/bind/zones", "Path to master bind zones directory"),

    "default_web_machine": ("localhost", "Default web machine for new accounts. (must be in Machines table)"),
    "default_mail_machine": ("localhost", "Default mail machine for new accounts. (must be in Machines table)"),
    "default_mysql_machine": ("localhost", "Default mysql machine for new accounts. (must be in Machines table)"),
    "default_pgsql_machine": ("localhost", "Default pgsql machine for new accounts. (must be in Machines table)"),

    "pgsql_server": ("localhost", "PostgreSQL server hostname"),
    "mysql_server": ("localhost", "MySQL server hostname"),

    "mysql_bind": ("localhost", "Host for mysql's users"),

    "email_server": ("127.0.0.1", "E-mail server"),
    "email_uid": (117, "Email UID"),
    "email_gid": (117, "Email GID"),

    "credit_wsgi": (1.0, "Credits for WSGI"),
    "credit_wsgi_proc": (0.2, "Credits for extra WSGI process"),
    "credit_php": (1.0, "Credits for PHP"),
    "credit_static": (0.25, "Credits for static"),
    "credit_fee": (3.0, "Credits for fee"),
    "credit_description": ("1 kr. = 2 Kč", "Credit description"),
    "credit_currency": ("CZK", "Currency"),
    "credit_quotient": (0.5, "Credit/currency Quotient"),
    "credit_threshold": (-7, "When should be a web disabled"),
    "credit_registration": (30, "Credits for registration"),
    "tax": (0, "%"),

    "terms_url": ("", "Terms URL"),

    "find_directory_deep":(2, "Finding directory deep"),

    "auto_disable":(True, "Auto disabling users"),
    "pagination":(50, "Pagination"),

    "var_symbol_prefix": (10, "Variable symbol prefix"),
    "bank_name": ("FIO Banka", "Name of your bank"),
    "bank_account": ("2200331030/2010", "Bank account number"),

    "pcp_invoices_api_url": ("http://faktury.initd.cz/invoice/api/new_invoice/", "PCP Invoices API URL"),
    "pcp_invoices_api_key": ("", "PCP Invoices API KEY"),
    "pcp_invoices_item_desc": ("Kredit hostingové služby Roští.cz", "Item description on invoice"),
    "pcp_invoices_item_unit": ("ks", "Item unit on invoice"),
    
    "pcp_runner_path": ("/usr/local/bin/pcp_runner", "PCP Runner path"),
    }
