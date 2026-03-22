"""Tests for OWASP input validation."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from httpx import AsyncClient

from presidio_fastapi.validation import check_owasp


class TestCheckOwasp:
    def test_clean_input_passes(self) -> None:
        check_owasp("hello world")
        check_owasp({"name": "alice", "age": "30"})
        check_owasp(["item1", "item2"])

    def test_sql_injection_blocked(self) -> None:
        with pytest.raises(HTTPException, match="SQL injection"):
            check_owasp("'; DROP TABLE users;--")

    def test_sql_union_select_blocked(self) -> None:
        with pytest.raises(HTTPException, match="SQL injection"):
            check_owasp("1 UNION SELECT * FROM passwords")

    def test_xss_script_blocked(self) -> None:
        with pytest.raises(HTTPException, match="XSS"):
            check_owasp('<script>alert("xss")</script>')

    def test_xss_img_blocked(self) -> None:
        with pytest.raises(HTTPException, match="XSS"):
            check_owasp("<img src=x onerror=alert(1)>")

    def test_path_traversal_blocked(self) -> None:
        with pytest.raises(HTTPException, match="Path traversal"):
            check_owasp("../../etc/passwd")

    def test_nested_dict_blocked(self) -> None:
        with pytest.raises(HTTPException, match="SQL injection"):
            check_owasp({"query": "'; DROP TABLE users;--"})

    def test_nested_list_blocked(self) -> None:
        with pytest.raises(HTTPException, match="XSS"):
            check_owasp(["safe", '<script>alert("x")</script>'])


class TestValidationEndpoint:
    @pytest.mark.asyncio
    async def test_echo_blocks_sql_injection(self, client: AsyncClient) -> None:
        resp = await client.post("/echo", json={"q": "'; DROP TABLE users;--"})
        assert resp.status_code == 400
        assert "SQL injection" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_echo_blocks_xss(self, client: AsyncClient) -> None:
        resp = await client.post("/echo", json={"q": "<script>alert(1)</script>"})
        assert resp.status_code == 400
        assert "XSS" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_echo_passes_clean_data(self, client: AsyncClient) -> None:
        resp = await client.post("/echo", json={"message": "hello"})
        assert resp.status_code == 200
        assert resp.json()["message"] == "hello"
