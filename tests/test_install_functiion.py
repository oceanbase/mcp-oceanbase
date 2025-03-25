from oceanbase_install import ob_install_function


def test_generate_ob_config():
    # 部署参数配置
    servers = [
        ("172.19.33.2", "zone1"),
        ("172.19.33.3", "zone2"),
        ("172.19.33.4", "zone3")
    ]

    global_config = {
        "memory_limit": "6G",
        "system_memory": "1G",
        "datafile_size": "2G",
        "datafile_next": "2G",
        "datafile_maxsize": "20G",
        "log_disk_size": "14G",
        "cpu_count": 16,
        "production_mode": False,
        "enable_syslog_wf": False,
        "max_syslog_file_count": 4
    }

    server_common_config = {
        "mysql_port": 2881,
        "rpc_port": 2882,
        "obshell_port": 2886,
        "home_path": "/root/observer"
    }

    user_config = {
        "username": "admin",
        "password": "your_password",
        "port": 22,
        "timeout": 30
    }

    # 生成配置
    ob_config = ob_install_function.generate_ob_config(
        servers=servers,
        global_config=global_config,
        server_common_config=server_common_config,
        user_config=user_config
    )
    server1 = ob_config.get("oceanbase-ce").get("servers")[0].get("name")
    assert server1 == "server1"
