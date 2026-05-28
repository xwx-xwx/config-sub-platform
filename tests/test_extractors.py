import pytest
from app.extractors.links import extract_links, extract_links_from_text


def test_extract_vmess():
    links = extract_links_from_text("vmess://eyJhZGQiOiJleGFtcGxlLmNvbSJ9")
    assert len(links) == 1
    assert links[0].startswith("vmess://")


def test_extract_vless():
    links = extract_links_from_text("vless://uuid@example.com:443")
    assert len(links) == 1
    assert links[0].startswith("vless://")


def test_extract_trojan():
    links = extract_links_from_text("trojan://password@example.com:443")
    assert len(links) == 1
    assert links[0].startswith("trojan://")


def test_extract_ss():
    links = extract_links_from_text("ss://YWVzLTI1Ni1nY206cGFzc3dAMTk0LjU2LjEwLjEwMDo4ODg4")
    assert len(links) == 1
    assert links[0].startswith("ss://")


def test_extract_multiple():
    text = "vmess://abc vless://def trojan://ghi"
    links = extract_links_from_text(text)
    assert len(links) == 3


def test_extract_no_links():
    assert extract_links_from_text("no links here") == []


def test_extract_malformed():
    assert extract_links_from_text("vmess://") == []


def test_extract_from_list():
    result = extract_links(["vmess://abc", "vless://def"])
    assert len(result) == 2
