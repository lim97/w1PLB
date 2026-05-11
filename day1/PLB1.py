import os
import random
from dotenv import load_dotenv
load_dotenv()
#환경 변수 로드
admin= os.getenv("ADMIN_NAME","Guest")

#데이터 선언
whitelist = ("192.168.1.10","192.168.1.11")
server_assets=[
    {"name": "WEB-01", "ip" : "192.168.1.10", "status": "Run"},
    {"name": "DB-01", "ip" : "192.168.1.20", "status": "Stop"}
]

#사용자 입력 , 수치 시뮬레이션
new_name=input("새로운 서버 이름 :")
new_ip=input("추가할 서버 :")
new_server = {}
new_server["name"] = new_name
new_server["ip"] = new_ip
new_server["status"] = "RUN"
new_server["cpu"]= random.uniform(0.0,100.0)

#입력 받은 서버 추가
server_assets.append(new_server)

#상태 업데이트 
server_assets[0]["status"] ="Stop"

#server_assets 마지막
last= len(server_assets)-1
    
#포멧팅
print(f"총 {len(server_assets)}대의 서버의 보안 점검 시작합니다")
print("--------------------------------------------")

print(f"[담당자:{admin}]{server_assets[0]['name']}서버({server_assets[0]['status']})점검 수행")
print(f"-화이트 리스트 대상 여부 :{server_assets[0]['ip'] in whitelist}")
print("--------------------------------------------")

print(f"[담당자:{admin}]{server_assets[1]['name']}서버({server_assets[1]['status']})점검 수행")
print(f"-화이트 리스트 대상 여부 :{server_assets[1]['ip'] in whitelist}")
print("--------------------------------------------")

print(f"[담당자:{admin}]{server_assets[last]['name']}서버({server_assets[last]['status']})점검 수행")
print(f"-화이트 리스트 대상 여부 :{server_assets[last]['ip'] in whitelist} /현재 부하 :{server_assets[last]['cpu']:.1f}%")
print("--------------------------------------------")

