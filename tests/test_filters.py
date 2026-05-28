import pytest
from app.models.config import ProxyConfig
from app.filters.mix import mix_filter
from app.filters.cloudflare_filter import cloudflare_filter
from app.filters.reality_filter import reality_filter
from app.filters.mobile import mobile_filter
from app.filters.fast_filter import fast_filter
from app.filters.clean import clean_filter


def make_cfg(protocol="vmess", host="a.com", port=443, uuid="u", score=0, **kw):
    return ProxyConfig(
        protocol=protocol, host=host, port=port, uuid=uuid, score=score, **kw
    )


def test_mix_filter_respects_limit():
    configs = [make_cfg(score=i) for i in range(500)]
    result = mix_filter(configs)
    assert len(result) == 300
    assert result[0].score == 499
    assert result[-1].score == 200


def test_cloudflare_filter_only_cloudflare():
    cf = make_cfg(host="1.1.1.1", tls=True, transport="ws", score=100)
    non_cf = make_cfg(host="other.com", score=100)
    result = cloudflare_filter([cf, non_cf])
    assert len(result) == 1
    assert result[0].host == "1.1.1.1"


def test_reality_filter_only_reality():
    r = make_cfg(protocol="vless", reality=True, score=100)
    non_r = make_cfg(score=100)
    result = reality_filter([r, non_r])
    assert len(result) == 1
    assert result[0].reality is True


def test_clean_filter_removes_garbage():
    good = make_cfg(host="good.com", score=10, uuid="valid")
    bad_host = make_cfg(host="localhost", score=10, uuid="valid")
    bad_score = make_cfg(host="good.com", score=-10, uuid="valid")
    no_cred = make_cfg(host="good.com", score=10, uuid=None)
    result = clean_filter([good, bad_host, bad_score, no_cred])
    assert len(result) == 1
    assert result[0].host == "good.com"


def test_mobile_filter_prefers_ws():
    ws = make_cfg(transport="ws", score=0)
    tcp = make_cfg(transport="tcp", score=0)
    result = mobile_filter([tcp, ws])
    assert len(result) == 2
    assert result[0].transport == "ws"


def test_fast_filter_top_scores():
    configs = [make_cfg(score=i) for i in range(100)]
    result = fast_filter(configs)
    assert len(result) == 50
    assert result[0].score == 99
