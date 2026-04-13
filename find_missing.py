import re
import urllib.request
import ssl

with open('downloaded_packets.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = re.compile(r'<A HREF="/packets/index\.php\?Packet=([^"]+)" class="pkt(Both|Client|Server)">\[([^\]]+)\] ([^<]+)</A>')
pol_packets = []
for match in pattern.finditer(html):
    pkt_id_str = match.group(1).upper()
    cat = match.group(2).lower()
    name = match.group(4)
    pkt_id_hex = pkt_id_str.replace("0X", "").zfill(2)
    pol_packets.append({'id': pkt_id_hex, 'cat': cat, 'name': name, 'url_id': match.group(1)})

with open('index.html', 'r', encoding='utf-8', errors='ignore') as f:
    idx_content = f.read()

idx_pattern = re.compile(r'<a href="#(client|server|both|unknown)([A-F0-9\.]+)">(.*?)</a>', re.IGNORECASE)
existing_ids = set()
for match in idx_pattern.finditer(idx_content):
    cat = match.group(1).lower()
    pid = match.group(2).upper()
    existing_ids.add((cat, pid))

missing = []
for p in pol_packets:
    found = False
    for cat, pid in existing_ids:
        # Ignore subcommands to match main base ID
        base_id = pid.split('.')[0]
        if base_id == p['id']:
            found = True
            break
    if not found:
        missing.append(p)

print(f"Total POL: {len(pol_packets)}")
print(f"Total Existing: {len(existing_ids)}")
print(f"Missing count: {len(missing)}")
for m in missing:
    print(m)
