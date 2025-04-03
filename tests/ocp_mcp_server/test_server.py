import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

from ocp_mcp_server.server import ADDRESS, AK, SK, query_ocp_api


def test_example():
    assert 1 + 1 == 2


def test_query_ocp_api_basic():
    """测试基本的 API 请求功能"""
    resp = query_ocp_api(
        "GET",
        "",
        "/api/v2/monitor/metricsWithLabel",
        {
            "labels": "app:ob",
            "groupBy": ["app", "ob_cluster_id"],
            "metrics": ["cpu_percent"],
            "endTime": "2025-03-28T16:20:48+08:00",
            "interval": 60,
            "startTime": "2025-03-28T16:15:48+08:00",
        },
    )

    assert json.loads(resp)["status"] == 200
