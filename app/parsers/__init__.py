from app.parsers.vmess import parse_vmess
from app.parsers.vless import parse_vless
from app.parsers.trojan import parse_trojan
from app.parsers.shadowsocks import parse_shadowsocks

PARSERS = {
    "vmess": parse_vmess,
    "vless": parse_vless,
    "trojan": parse_trojan,
    "ss": parse_shadowsocks,
}


def parse_link(link: str):
    protocol = link.split("://")[0] if "://" in link else ""
    parser = PARSERS.get(protocol)
    if parser:
        return parser(link)
    return None
