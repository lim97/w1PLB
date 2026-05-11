from pathlib import Path
import csv
import json

log_data = """2026-04-06|10:01:22|192.168.1.10|10.0.0.1|443|ALLOW
-2026-04-06|10:05:45|211.23.45.10|10.0.0.2|22|BLOCK
-2026-04-06|10:12:10|192.168.1.20|10.0.0.1|80|ALLOW
-2026-04-06|10:15:33|10.0.0.55|10.10.0.1|3389|BLOCK
-2026-04-06|10:20:01|127.0.0.1|127.0.0.1|8080|ALLOW
"""
Path("day3/firewall_access.log").write_text(log_data, encoding="utf-8-sig")



ip_set = set()

with open("day3/firewall_access.log", "r", encoding="utf-8-sig") as f:
    for line in f.read().strip().split("\n"):
        parts = line.split("|")
        if len(parts) == 6:
            ip_set.add(parts[2])


# 3. 필터 + 리포트 생성
def is_allowed(ip_set):
    whitelist = ("192.168.1.10", "192.168.1.20", "127.0.0.1")

    filtered = list(filter(lambda x: x not in whitelist, ip_set))

    
    json_data = list(map(lambda x: {
        "Detected_IP": x,
        "Risk_Level": "High",
        "Status": None
    }, filtered))

   
    csv_data = list(map(lambda x: {
        "Detected_IP": x,
        "Risk_Level": "High"
    }, filtered))

  
    with open("day3/unauthorized_ips.csv", "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["Detected_IP", "Risk_Level"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_data)

    with open("day3/security_alert.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


is_allowed(ip_set)