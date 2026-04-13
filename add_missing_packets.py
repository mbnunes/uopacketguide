import re
import urllib.request
import time
from html import escape

# 1. Gather missing packets from find_missing.py logic
with open('downloaded_packets.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = re.compile(r'<A HREF="/packets/index\.php\?Packet=([^"]+)" class="pkt(Both|Client|Server)">\[([^\]]+)\] ([^<]+)</A>')
pol_packets = []
for match in pattern.finditer(html):
    pkt_id_str = match.group(1).upper()
    cat = match.group(2).lower()
    name = match.group(4)
    pkt_id_hex = pkt_id_str.replace("0X", "").zfill(2)
    pol_packets.append({'id': pkt_id_hex, 'cat': cat, 'name': name, 'url': "https://docs.polserver.com/packets/index.php?Packet="+match.group(1)})

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
        base_id = pid.split('.')[0]
        if base_id == p['id']:
            found = True
            break
    if not found:
        missing.append(p)

print(f"Missing packets count: {len(missing)}")

def fetch_packet_details(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            page = response.read().decode('utf-8')
            return page
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_packet_size(page_html):
    # Size: Variable<BR /> or Size: 104 bytes<BR />
    m = re.search(r'Size:\s*(.*?)\s*<BR />', page_html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Unknown"

def parse_packet_build(page_html):
    # Extract stuff between <B>Packet Build</B><BR /> and </P>
    build_pattern = re.search(r'<B>Packet Build</B><BR />(.*?)</P>', page_html, re.IGNORECASE | re.DOTALL)
    if not build_pattern:
        return []
    
    lines = build_pattern.group(1).split('<br/>')
    build_items = []
    for line in lines:
        line = line.replace('<br>', '').replace('<BR/>', '').replace('<BR />', '').strip()
        if not line:
            continue
        # Expected format: BYTE[1]   Command  or SHORT[2]  value
        # Use regex to split out type/size and description
        m = re.match(r'^([A-Z]+)\[(\d+|.*?)\].*?(.*?)$', line, re.IGNORECASE)
        if m:
            dtype = m.group(1).upper()
            size = m.group(2)
            desc = m.group(3).strip()
            # Map type
            if dtype == 'BYTE' and size == '1': html_type = 'byte'
            elif (dtype == 'BYTE' or dtype == 'SHORT') and size == '2': html_type = 'word'
            elif dtype == 'BYTE' and size == '4': html_type = 'dword'
            elif dtype == 'BYTE': html_type = f'char[{size}]'
            elif dtype == 'CHAR': html_type = f'char[{size}]'
            elif dtype == 'SHORT': html_type = f'word[{size}]'
            elif dtype == 'INT': html_type = f'dword[{size}]'
            else: html_type = f'{dtype.lower()}[{size}]'
            build_items.append((html_type, desc))
        else:
            # Maybe just some text
            build_items.append(("unknown", line))
    return build_items

def generate_packet_html(pkt, size_str, build_items):
    cat_id = f"{pkt['cat']}{pkt['id']}"
    cat_disp = pkt['cat'].capitalize()
    html = f"""
        <br><a href="#top" style="float:right;">↑</a><span id="{cat_id}"></span>
        <table style="border: 2px solid #808080; width:600px; background-color:#FFF8DC; border-collapse:collapse;">
            <tr>
                <td colspan="2" style="background-color: #FFD700; text-align: right;">{pkt['id']} - {escape(pkt['name'])}</td>
            </tr>
            <tr>
                <td colspan="2">
                    <div style="display: inline; float: left;">Added from POL Docs.<br>{escape(size_str)}</div>
                    <div style="display: inline; float: right;">from {pkt['cat']}</div>
                </td>
            </tr>"""
    for dtype, desc in build_items:
        html += f"""
            <tr>
                <td style="border-style: solid none solid solid; border-width:1px; border-color:#808080; width:70px;">{escape(dtype)}</td>
                <td style="border-style: solid solid solid none; border-width: 1px; border-color: #808080; width:524px;">{escape(desc)}</td>
            </tr>"""
    html += """
        </table>"""
    return html

new_toc_items = {'client': [], 'server': [], 'both': []}
new_body_html = ""

for p in missing:
    print(f"Fetching {p['id']} - {p['name']}...")
    page_html = fetch_packet_details(p['url'])
    size_str = parse_packet_size(page_html)
    build_items = parse_packet_build(page_html)
    
    # Store TOC item
    cat_id = f"{p['cat']}{p['id']}"
    new_toc_items[p['cat']].append(f'            <tr>\n                <td><a href="#{cat_id}">{p["id"]} - {escape(p["name"])}</a></td>\n            </tr>')
    
    # Append to body
    new_body_html += generate_packet_html(p, size_str, build_items) + "\n"
    time.sleep(0.1)

# Modify the Table of Contents dynamically
# For each category, find its header, and append the new <tr> elements before the next category.
idx_content_lines = idx_content.split('\n')

final_lines = []
cat_marker_map = {"Client:": "client", "Server:": "server", "Both:": "both", "Unknown:": "unknown"}
current_cat = None

i = 0
while i < len(idx_content_lines):
    line = idx_content_lines[i]
    final_lines.append(line)
    
    if "<td>Client:</td>" in line:
        current_cat = "client"
    elif "<td>Server:</td>" in line:
        current_cat = "server"
    elif "<td>Both:</td>" in line:
        current_cat = "both"
    elif "<td>Unknown:</td>" in line:
        current_cat = "unknown"
    
    # Before we close the table of contents </table>, or before we move to the next category, insert new items
    # Wait, the structure is just <tr><td>...</td></tr> items under each category header.
    # To append to a category, we find the NEXT category header, or </table>, and insert before it.
    if current_cat in ['client', 'server', 'both']:
        # check if next line is another category or end of table
        next_line = idx_content_lines[i+1] if i+1 < len(idx_content_lines) else ""
        if "<td>Server:</td>" in next_line or "<td>Both:</td>" in next_line or "<td>Unknown:</td>" in next_line or "</table>" in next_line:
            # Insert the new items for current_cat
            for toc_item in new_toc_items[current_cat]:
                final_lines.extend(toc_item.split('\n'))
            new_toc_items[current_cat] = [] # empty to avoid double insertion

    if '</body>' in line:
        break
    i += 1

# Oh wait, we need to insert new_body_html before </body> or right before the end
# But wait, final_lines includes </body> already if we used the break above?
# We need to reconstruct properly. Let's just find the closing </body> tag and insert before it.
# Let's fix the logic: just read all lines, insert TOC elements in place, and append new body before </body>.

def inject_all():
    lines = idx_content.split('\n')
    out = []
    curr_cat = None
    for j, line in enumerate(lines):
        if "<td>Client:</td>" in line:
            curr_cat = "client"
        elif "<td>Server:</td>" in line:
            curr_cat = "server"
        elif "<td>Both:</td>" in line:
            curr_cat = "both"
        elif "<td>Unknown:</td>" in line:
            curr_cat = "unknown"
            
        out.append(line)
        
        if curr_cat in ['client', 'server', 'both']:
            # lookahead for the end of this section
            nl = lines[j+1] if j+1 < len(lines) else ""
            if "<td>Server:</td>" in nl or "<td>Both:</td>" in nl or "<td>Unknown:</td>" in nl or "</table>" in nl:
                if len(new_toc_items[curr_cat]) > 0:
                    for toc_item in new_toc_items[curr_cat]:
                        out.extend(toc_item.split('\n'))
                    new_toc_items[curr_cat] = []
                    
        if "</body>" in line:
            # We inserted '</body>', let's remove it and insert the new_body_html FIRST
            out.pop()
            out.extend(new_body_html.split('\n'))
            out.append("    </body>")
            
    return '\n'.join(out)

new_content = inject_all()
with open('index_updated.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Finished writing index_updated.html")
