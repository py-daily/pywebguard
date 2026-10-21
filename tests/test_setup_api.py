"""
Tests for the short setup API: rate strings, install(), dict config and the
default storage for FastAPIGuard.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from flask import Flask

from pywebguard import AsyncGuard, FastAPIGuard, FlaskGuard, Guard, GuardConfig
from pywebguard.storage.memory import AsyncMemoryStorage, MemoryStorage
from pywebguard.utils.setup import (
    build_install_config,
    parse_rate,
    route_limits_to_list,
)


class TestParseRate:
    @pytest.mark.parametrize(
        "rate, expected",
        [
            ("100/minute", 100),
            ("5/second", 300),
            (" 7 / MINUTE ", 7),
        ],
    )
    def test_valid(self, rate, expected):
        assert parse_rate(rate) == expected

    @pytest.mark.parametrize(
        "rate", ["abc", "0/minute", "5/day", "5/hour", "/minute", "5", "", None, 5]
    )
    def test_invalid(self, rate):
        with pytest.raises(ValueError):
            parse_rate(rate)


class TestRouteLimits:
    def test_mapping_converts_to_list_format(self):
        assert route_limits_to_list(
            {"/api/limited": "5/minute", "/api/admin/**": "20/minute"}
        ) == [
            {"endpoint": "/api/limited", "requests_per_minute": 5, "burst_size": 0},
            {"endpoint": "/api/admin/**", "requests_per_minute": 20, "burst_size": 0},
        ]

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            route_limits_to_list({"/x": "fast"})


class TestBuildInstallConfig:
    def test_defaults_only_enable_rate_limiting(self):
        config = build_install_config()
        assert config.rate_limit.enabled
        assert not config.user_agent.enabled
        assert not config.ip_filter.enabled
        assert not config.cors.enabled
        assert not config.penetration.enabled

    def test_flat_options_enable_their_sections(self):
        config = build_install_config(
            rate_limit="100/minute",
            blocked_agents=["curl"],
            ip_whitelist=["127.0.0.1"],
            ip_blacklist=["10.0.0.0/8"],
            cors_origins=["https://example.com"],
        )
        assert config.rate_limit.requests_per_minute == 100
        assert config.rate_limit.burst_size == 0
        assert config.user_agent.enabled
        assert config.user_agent.blocked_agents == ["curl"]
        assert config.ip_filter.enabled
        assert config.ip_filter.whitelist == ["127.0.0.1"]
        assert config.ip_filter.blacklist == ["10.0.0.0/8"]
        assert config.cors.enabled
        assert config.cors.allow_origins == ["https://example.com"]

    def test_config_is_used_as_given(self):
        given = GuardConfig(rate_limit={"requests_per_minute": 7})
        assert build_install_config(config=given) is given

    def test_dict_config_is_validated(self):
        config = build_install_config(config={"rate_limit": {"requests_per_minute": 7}})
        assert isinstance(config, GuardConfig)
        assert config.rate_limit.requests_per_minute == 7

    def test_flat_options_with_config_raise(self):
        with pytest.raises(ValueError, match="rate_limit"):
            build_install_config(config=GuardConfig(), rate_limit="5/minute")

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            build_install_config(rate_limit="soon")


class TestDictConfig:
    def test_guard_accepts_dict(self):
        guard = Guard(config={"rate_limit": {"requests_per_minute": 7}})
        assert guard.config.rate_limit.requests_per_minute == 7

    def test_async_guard_accepts_dict(self):
        guard = AsyncGuard(config={"rate_limit": {"requests_per_minute": 7}})
        assert guard.config.rate_limit.requests_per_minute == 7

    def test_invalid_dict_raises_validation_error(self):
        with pytest.raises(ValueError):
            Guard(config={"rate_limit": {"requests_per_minute": 0}})

    def test_guard_config_instance_still_works(self):
        config = GuardConfig(rate_limit={"requests_per_minute": 7})
        assert Guard(config=config).config is config

    def test_flask_guard_accepts_dict(self):
        guard = FlaskGuard(config={"rate_limit": {"requests_per_minute": 7}})
        assert guard.guard.config.rate_limit.requests_per_minute == 7

    def test_fastapi_guard_accepts_dict(self):
        guard = FastAPIGuard(
            FastAPI(),
            config={"rate_limit": {"requests_per_minute": 7}},
            storage=AsyncMemoryStorage(),
        )
        assert guard.guard.config.rate_limit.requests_per_minute == 7


class TestFastAPIDefaultStorage:
    def test_no_storage_defaults_to_memory_with_warning(self):
        with pytest.warns(UserWarning, match="in-memory"):
            guard = FastAPIGuard(FastAPI(), config=GuardConfig())
        assert isinstance(guard.guard.storage, AsyncMemoryStorage)

    def test_explicit_storage_does_not_warn(self, recwarn):
        FastAPIGuard(FastAPI(), config=GuardConfig(), storage=AsyncMemoryStorage())
        assert not [w for w in recwarn if "in-memory" in str(w.message)]

    def test_sync_storage_still_raises(self):
        with pytest.raises(ValueError, match="AsyncBaseStorage"):
            FastAPIGuard(FastAPI(), config=GuardConfig(), storage=MemoryStorage())


def _fastapi_app(**options) -> TestClient:
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"ok": True}

    @app.get("/api/limited")
    async def limited():
        return {"ok": True}

    FastAPIGuard.install(app, **options)
    return TestClient(app)


@pytest.mark.filterwarnings("ignore:No storage given")
class TestFastAPIInstall:
    def test_warns_about_memory_storage_when_app_starts(self):
        client = _fastapi_app()
        with pytest.warns(UserWarning, match="in-memory"):
            client.get("/")

    def test_default_rate_limit_applies(self):
        client = _fastapi_app(rate_limit="2/minute")
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 429

    def test_route_limits_override_default(self):
        client = _fastapi_app(
            rate_limit="100/minute", route_limits={"/api/limited": "1/minute"}
        )
        assert client.get("/api/limited").status_code == 200
        assert client.get("/api/limited").status_code == 429
        assert client.get("/").status_code == 200

    def test_blocked_agents(self):
        client = _fastapi_app(blocked_agents=["evilbot"])
        assert client.get("/", headers={"User-Agent": "EvilBot/1.0"}).status_code == 403
        assert client.get("/", headers={"User-Agent": "firefox"}).status_code == 200

    def test_empty_user_agent_allowed_without_blocked_agents(self):
        client = _fastapi_app()
        assert client.get("/", headers={"User-Agent": ""}).status_code == 200

    def test_penetration_detection_off_by_default(self):
        client = _fastapi_app()
        assert client.get("/?q=<script>alert(1)</script>").status_code == 200

    def test_config_with_flat_options_raises(self):
        with pytest.raises(ValueError, match="not both"):
            FastAPIGuard.install(FastAPI(), config=GuardConfig(), rate_limit="5/minute")

    def test_invalid_rate_raises_before_registering(self):
        with pytest.raises(ValueError):
            FastAPIGuard.install(FastAPI(), rate_limit="fast")


def _flask_app(**options) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def root():
        return {"ok": True}

    @app.route("/api/limited")
    def limited():
        return {"ok": True}

    FlaskGuard.install(app, **options)
    return app


class TestFlaskInstall:
    def test_returns_registered_extension(self):
        app = Flask(__name__)
        guard = FlaskGuard.install(app, rate_limit="5/minute")
        assert isinstance(guard, FlaskGuard)
        assert app.config["PYWEBGUARD"] is guard

    def test_default_rate_limit_applies(self):
        client = _flask_app(rate_limit="2/minute").test_client()
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/").status_code == 429

    def test_route_limits_override_default(self):
        client = _flask_app(
            rate_limit="100/minute", route_limits={"/api/limited": "1/minute"}
        ).test_client()
        assert client.get("/api/limited").status_code == 200
        assert client.get("/api/limited").status_code == 429
        assert client.get("/").status_code == 200

    def test_blocked_agents(self):
        client = _flask_app(blocked_agents=["evilbot"]).test_client()
        assert client.get("/", headers={"User-Agent": "EvilBot/1.0"}).status_code == 403
        assert client.get("/", headers={"User-Agent": "firefox"}).status_code == 200

    def test_config_with_flat_options_raises(self):
        with pytest.raises(ValueError, match="not both"):
            FlaskGuard.install(
                Flask(__name__), config=GuardConfig(), cors_origins=["*"]
            )
