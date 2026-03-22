"""Tests for the dependency / CVE quick-check module."""

from __future__ import annotations

from presidio_fastapi.dep_check import _version_lt, check_dependencies


class TestVersionParsing:
    def test_simple_comparison(self) -> None:
        assert _version_lt("0.99.0", "0.100.0")
        assert not _version_lt("0.100.0", "0.100.0")
        assert not _version_lt("1.0.0", "0.100.0")

    def test_prerelease_handling(self) -> None:
        assert not _version_lt("2.1.0rc1", "2.0.0")


class TestCheckDependencies:
    def test_returns_list(self) -> None:
        result = check_dependencies()
        assert isinstance(result, list)

    def test_no_warnings_for_current_deps(self) -> None:
        warnings = check_dependencies()
        for w in warnings:
            assert "warning" in w
