#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
speedtest_nodes.py — 从多个免费订阅源拉取节点，逐节点实测（延迟+下载速度），
输出 Top N 优选节点列表（供飞牛 xray_autoupdate 拉取使用）。

运行环境：GitHub Actions（ubuntu-latest），可直连 GitHub/外网。
用法：python3 speedtest_nodes.py [--top 20] [--output generated/nodes_top20.txt]
"""
import base64, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, zipfile, concurrent.futures, argparse, socket

# ---------- 配置 ----------
SOURCES = [  # 免费订阅源（GitHub raw，Actions 环境可直连）
    "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/v2ray-base64.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_base64.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
]
XRAY_ZIP = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip"
TEST_URL = "https://speed.cloudflare.com/__down?bytes=2000000"  # 2MB 下载测速
TEST_HEAD = 1048576  # 测速下载量（1MB，避免耗时过长）
CONCURRENCY = 8
PROBE_TIMEOUT = 25
LOG = True

def log(msg):
    if LOG:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# ---------- 订阅拉取与解析 ----------
def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def parse_subscription(text):
    """从订阅文本提取节点链接行（vless/vmess/ss/trojan/hy2）"""
    nodes = []
    text = text.strip()
    if not text:
        return nodes
    # 可能是 base64 整体订阅
    if not any(text.startswith(p) for p in ("vless://", "vmess://", "ss://", "trojan://", "hy2://", "hysteria2://")):
        try:
            padded = text + "=" * ((4 - len(text) % 4) % 4)
            decoded = base64.b64decode(padded).decode("utf-8", "ignore")
            if any(decoded.startswith(p) for p in ("vless://", "vmess://", "ss://", "trojan://", "hy2://")):
                text = decoded
        except Exception:
            pass
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("vless://", "vmess://", "ss://", "trojan://", "hy2://", "hysteria2://")):
            nodes.append(line)
    return nodes

def parse_node(link):
    """解析节点链接 → (protocol, xray_outbound_dict, name)"""
    try:
        if link.startswith("vless://"):
            m = re.match(r"vless://([^@]+)@([^:]+):(\d+)\?(.*?)(?:#(.*))?$", link)
            if not m: return None
            uid, host, port, params, name = m.groups()
            p = dict(re.findall(r"([^&=]+)=([^&]*)", params))
            out = {"protocol": "vless", "tag": name or host,
                   "settings": {"vnext": [{"address": host, "port": int(port),
                                           "users": [{"id": uid, "encryption": "none"}]}]}}
            stream = {}
            net = p.get("type", "tcp")
            if net in ("ws", "websocket"):
                stream["network"] = "ws"
                ws = {}
                if p.get("path"): ws["path"] = p["path"]
                if p.get("host"): ws["headers"] = {"Host": p["host"]}
                stream["wsSettings"] = ws
            elif net == "grpc":
                stream["network"] = "grpc"
                stream["grpcSettings"] = {"serviceName": p.get("serviceName", ""), "multiMode": False}
            else:
                stream["network"] = "tcp"
            if p.get("security") in ("tls", "reality") or "sni" in p:
                if p.get("security") == "reality":
                    stream["security"] = "reality"
                    stream["realitySettings"] = {"serverName": p.get("sni", ""), "fingerprint": p.get("fp", "chrome"),
                                                 "show": False, "publicKey": p.get("pbk", ""), "shortId": p.get("sid", "")}
                else:
                    stream["security"] = "tls"
                    stream["tlsSettings"] = {"serverName": p.get("sni", host), "allowInsecure": True,
                                             "fingerprint": p.get("fp", "chrome")}
            if stream:
                out["streamSettings"] = stream
            return ("vless", out, name or host)

        if link.startswith("vmess://"):
            b64 = link[len("vmess://"):].split("#")[0]
            if "@" in b64:  # 非标准格式
                return None
            cfg = json.loads(base64.b64decode(b64 + "=" * ((4 - len(b64) % 4) % 4)).decode("utf-8", "ignore"))
            out = {"protocol": "vmess", "tag": cfg.get("ps", cfg.get("add", "")),
                   "settings": {"vnext": [{"address": cfg.get("add", ""), "port": int(cfg.get("port", 0)),
                                           "users": [{"id": cfg.get("id", ""), "alterId": int(cfg.get("aid", 0)),
                                                      "security": "auto"}]}]}}
            stream = {"network": cfg.get("net", "tcp")}
            if stream["network"] == "ws":
                stream["wsSettings"] = {"path": cfg.get("path", ""),
                                        "headers": {"Host": cfg.get("host", "")} if cfg.get("host") else {}}
            elif stream["network"] == "grpc":
                stream["grpcSettings"] = {"serviceName": cfg.get("path", ""), "multiMode": False}
            if cfg.get("tls") == "tls":
                stream["security"] = "tls"
                stream["tlsSettings"] = {"serverName": cfg.get("sni") or cfg.get("host") or cfg.get("add"),
                                         "allowInsecure": True}
            out["streamSettings"] = stream
            return ("vmess", out, cfg.get("ps", cfg.get("add", "")))

        if link.startswith("ss://"):
            rest = link[len("ss://"):]
            name = ""
            if "#" in rest:
                rest, name = rest.split("#", 1)
                name = urllib.parse.unquote(name)
            if "@" in rest:
                method_pass, host_port = rest.split("@", 1)
                mp = base64.b64decode(method_pass + "=" * ((4 - len(method_pass) % 4) % 4)).decode("utf-8", "ignore")
                method, password = mp.split(":", 1)
            else:
                try:
                    dec = base64.b64decode(rest + "=" * ((4 - len(rest) % 4) % 4)).decode("utf-8", "ignore")
                    method_pass, host_port = dec.split("@", 1)
                    method, password = method_pass.split(":", 1)
                except Exception:
                    return None
            host, port = host_port.rsplit(":", 1)
            out = {"protocol": "shadowsocks", "tag": name or host,
                   "settings": {"servers": [{"address": host, "port": int(port), "method": method,
                                             "password": password}]}}
            return ("ss", out, name or host)

        if link.startswith("trojan://"):
            m = re.match(r"trojan://([^@]+)@([^:]+):(\d+)\?(.*?)(?:#(.*))?$", link)
            if not m: return None
            pw, host, port, params, name = m.groups()
            p = dict(re.findall(r"([^&=]+)=([^&]*)", params))
            out = {"protocol": "trojan", "tag": name or host,
                   "settings": {"servers": [{"address": host, "port": int(port), "password": pw}]}}
            stream = {}
            if p.get("type", "tcp") == "ws":
                stream["network"] = "ws"
                stream["wsSettings"] = {"path": p.get("path", ""),
                                        "headers": {"Host": p.get("host", host)} if p.get("host") else {}}
            if p.get("security", "tls") == "tls":
                stream["security"] = "tls"
                stream["tlsSettings"] = {"serverName": p.get("sni", host), "allowInsecure": True}
            if stream:
                out["streamSettings"] = stream
            return ("trojan", out, name or host)
    except Exception as e:
        return None
    return None

# ---------- xray 与测速 ----------
def ensure_xray(tmpdir):
    """下载并解压 xray-core，返回 xray 可执行路径"""
    xray_bin = os.path.join(tmpdir, "xray")
    if os.path.exists(xray_bin):
        return xray_bin
    zip_path = os.path.join(tmpdir, "xray.zip")
    log(f"下载 Xray-core: {XRAY_ZIP}")
    urllib.request.urlretrieve(XRAY_ZIP, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        for f in z.namelist():
            if f.endswith("xray") or f == "xray":
                z.extract(f, tmpdir)
                os.chmod(os.path.join(tmpdir, f), 0o755)
    return xray_bin

def build_config(outbound):
    """生成单节点 xray 配置，随机 socks inbound 端口"""
    import random
    port = random.randint(20000, 60000)
    cfg = {
        "log": {"loglevel": "error"},
        "inbounds": [{"port": port, "protocol": "socks",
                      "settings": {"udp": True, "auth": "noauth"}}],
        "outbounds": [outbound,
                      {"protocol": "freedom", "tag": "direct"}],
    }
    return cfg, port

def probe_node(link, xray_bin, tmpdir):
    """测速单节点，返回 (speed_bps, latency_s, name) 或 None"""
    parsed = parse_node(link)
    if not parsed:
        return None
    proto, outbound, name = parsed
    try:
        cfg, port = build_config(outbound)
        cfg_path = os.path.join(tmpdir, f"cfg_{port}.json")
        with open(cfg_path, "w") as f:
            json.dump(cfg, f)
        proc = subprocess.Popen([xray_bin, "run", "-c", cfg_path],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(0.6)
            proxy = f"socks5h://127.0.0.1:{port}"
            # 延迟 + 下载测速
            t0 = time.time()
            speed = 0
            cmd = ["curl", "-s", "-m", str(PROBE_TIMEOUT), "-x", proxy,
                   "-r", f"0-{TEST_HEAD-1}", "-o", os.devnull, "-w", "%{speed_download}"]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=PROBE_TIMEOUT + 5)
                if r.returncode == 0 and r.stdout.strip():
                    speed = float(r.stdout.strip())
            except Exception:
                pass
            latency = time.time() - t0
            if speed > 1000:  # >1KB/s 才算可用
                return (speed, latency, name, proto)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
    except Exception:
        pass
    return None

# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=int(os.environ.get("TOP_N", "20")))
    ap.add_argument("--output", default="generated/nodes_top20.txt")
    ap.add_argument("--sources", default="")
    args = ap.parse_args()

    tmpdir = tempfile.mkdtemp(prefix="speedtest_")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # 1. 拉订阅
    all_links = []
    sources = args.sources.split(",") if args.sources else SOURCES
    for src in sources:
        try:
            text = fetch(src)
            nodes = parse_subscription(text)
            log(f"源 {src.split('/')[-1]}: {len(nodes)} 节点")
            all_links.extend(nodes)
        except Exception as e:
            log(f"源失败 {src}: {e}")
    all_links = list(dict.fromkeys(all_links))  # 去重
    log(f"去重后共 {len(all_links)} 节点")

    if not all_links:
        print("NO NODES")
        sys.exit(1)

    # 2. 下载 xray
    xray_bin = ensure_xray(tmpdir)
    log("xray 就绪")

    # 3. 并发测速
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(probe_node, l, xray_bin, tmpdir): l for l in all_links}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            done += 1
            r = fut.result()
            if r:
                results.append(r)
                log(f"[{done}/{len(all_links)}] ✓ {r[2][:30]} {r[0]/1024:.0f}KB/s")
            if done % 20 == 0:
                log(f"进度 {done}/{len(all_links)}")

    # 4. 排序输出
    results.sort(key=lambda x: -x[0])
    top = results[:args.top]
    log(f"可用 {len(results)}，输出 Top {len(top)}")

    lines = [f"# {time.strftime('%Y-%m-%d %H:%M')} | speed B/s | latency s | protocol | name", "# " + "-" * 60]
    for speed, lat, name, proto in top:
        lines.append(f"{int(speed)}\t{lat:.2f}\t{proto}\t{name}")
    with open(args.output, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"DONE top={len(top)} out={args.output}")

if __name__ == "__main__":
    import urllib.parse
    main()
