"""Testes unitários completos para o cliente HTTP do GitHub."""

import time
from unittest.mock import MagicMock, patch
import pytest
import requests

from lab03.src.cache_manager import CacheManager
from lab03.src.github_client import (
    GitHubClient,
    extract_page_number_from_url,
    parse_link_header,
)


def test_parse_link_header_valid():
    header = (
        '<https://api.github.com/repositories/123/contributors?per_page=1&anon=true&page=2>; rel="next", '
        '<https://api.github.com/repositories/123/contributors?per_page=1&anon=true&page=145>; rel="last"'
    )
    links = parse_link_header(header)
    assert "next" in links
    assert "last" in links
    assert links["next"] == "https://api.github.com/repositories/123/contributors?per_page=1&anon=true&page=2"
    assert links["last"] == "https://api.github.com/repositories/123/contributors?per_page=1&anon=true&page=145"


def test_parse_link_header_empty():
    assert parse_link_header(None) == {}
    assert parse_link_header("") == {}


def test_extract_page_number():
    url = "https://api.github.com/repos/owner/repo/contributors?per_page=1&anon=true&page=842"
    assert extract_page_number_from_url(url) == 842

    url_no_page = "https://api.github.com/repos/owner/repo/contributors"
    assert extract_page_number_from_url(url_no_page) is None


def test_client_initialization():
    client = GitHubClient(token="ghp_test_12345")
    assert client.session.headers["Authorization"] == "Bearer ghp_test_12345"
    assert "LabExperimentacao" in client.session.headers["User-Agent"]


def test_client_request_cache_hit(mock_cache: CacheManager):
    mock_cache.set("category_test", "key_1", {"hello": "world"})
    client = GitHubClient(token="test_token", cache_manager=mock_cache)

    data, headers = client.request(
        "repos/test/repo",
        cache_category="category_test",
        cache_key="key_1",
    )
    assert data == {"hello": "world"}


@patch("requests.Session.get")
def test_client_request_success_and_rate_limit_tracking(mock_get, mock_cache: CacheManager):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": 1, "name": "test-repo"}
    mock_resp.headers = requests.structures.CaseInsensitiveDict({
        "X-RateLimit-Limit": "5000",
        "X-RateLimit-Remaining": "4950",
        "X-RateLimit-Reset": "1700000000",
    })
    mock_get.return_value = mock_resp

    client = GitHubClient(token="test_token", cache_manager=mock_cache)
    data, headers = client.request(
        "repos/test/repo",
        cache_category="repos",
        cache_key="test_repo",
    )

    assert data == {"id": 1, "name": "test-repo"}
    assert client.last_rate_limit["remaining"] == 4950
    assert mock_cache.get("repos", "test_repo") == {"id": 1, "name": "test-repo"}


@patch("requests.Session.get")
def test_client_request_404_returns_none(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.headers = requests.structures.CaseInsensitiveDict()
    mock_get.return_value = mock_resp

    client = GitHubClient(token="test_token")
    data, headers = client.request("repos/invalid/notfound")
    assert data is None


@patch("requests.Session.get")
@patch("time.sleep")
def test_client_request_retry_on_500_then_success(mock_sleep, mock_get):
    mock_err = MagicMock()
    mock_err.status_code = 500
    mock_err.headers = requests.structures.CaseInsensitiveDict()

    mock_ok = MagicMock()
    mock_ok.status_code = 200
    mock_ok.json.return_value = {"recovered": True}
    mock_ok.headers = requests.structures.CaseInsensitiveDict({
        "X-RateLimit-Limit": "5000",
        "X-RateLimit-Remaining": "4900",
        "X-RateLimit-Reset": "1700000000",
    })

    mock_get.side_effect = [mock_err, mock_ok]

    client = GitHubClient(token="test_token", max_retries=2, backoff_factor=1.1)
    data, _ = client.request("repos/test/retry")
    assert data == {"recovered": True}
    assert mock_sleep.called


@patch("requests.Session.get")
@patch("time.sleep")
def test_client_request_rate_limited_retry(mock_sleep, mock_get):
    mock_rate = MagicMock()
    mock_rate.status_code = 403
    mock_rate.text = "API rate limit exceeded for user"
    mock_rate.headers = requests.structures.CaseInsensitiveDict({
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(time.time()) + 1),
    })

    mock_ok = MagicMock()
    mock_ok.status_code = 200
    mock_ok.json.return_value = {"after_rate_limit": True}
    mock_ok.headers = requests.structures.CaseInsensitiveDict({
        "X-RateLimit-Remaining": "5000",
        "X-RateLimit-Reset": "1700000000",
    })

    mock_get.side_effect = [mock_rate, mock_ok]

    client = GitHubClient(token="test_token", max_retries=2)
    data, _ = client.request("repos/test/rl")
    assert data == {"after_rate_limit": True}
    assert mock_sleep.called


@patch("requests.Session.get")
def test_get_rate_limit_status(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "resources": {
            "core": {"limit": 5000, "remaining": 4920, "reset": 1700000000}
        }
    }
    mock_get.return_value = mock_resp

    client = GitHubClient(token="test_token")
    status = client.get_rate_limit_status()
    assert status["remaining"] == 4920


@patch("requests.Session.get")
def test_paginate_multiple_pages(mock_get):
    # Página 1
    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {"items": [{"id": 1}, {"id": 2}]}
    resp1.headers = requests.structures.CaseInsensitiveDict({
        "Link": '<https://api.github.com/search/repositories?page=2>; rel="next"',
    })

    # Página 2
    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {"items": [{"id": 3}]}
    resp2.headers = requests.structures.CaseInsensitiveDict({})

    mock_get.side_effect = [resp1, resp2]

    client = GitHubClient(token="test_token")
    items = client.paginate("search/repositories")
    assert len(items) == 3
    assert [i["id"] for i in items] == [1, 2, 3]


@patch("requests.Session.get")
def test_count_contributors_with_link_header(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"login": "user1"}]
    mock_resp.headers = requests.structures.CaseInsensitiveDict({
        "Link": '<https://api.github.com/repos/owner/repo/contributors?per_page=1&anon=true&page=2>; rel="next", <https://api.github.com/repos/owner/repo/contributors?per_page=1&anon=true&page=350>; rel="last"',
        "X-RateLimit-Remaining": "4900",
    })
    mock_get.return_value = mock_resp

    client = GitHubClient(token="test_token")
    count = client.count_contributors("owner", "repo")
    assert count == 350


@patch("requests.Session.get")
def test_count_contributors_without_link_header(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"login": "solo_author"}]
    mock_resp.headers = requests.structures.CaseInsensitiveDict({})
    mock_get.return_value = mock_resp

    client = GitHubClient(token="test_token")
    count = client.count_contributors("owner", "repo")
    assert count == 1
