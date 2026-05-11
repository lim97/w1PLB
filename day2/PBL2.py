import random
server_names = [f"SVR-{i:2d}"for i in range(1,16)]
raw_logs = [random.randint(1,100) for _ in range(10)] + [0,"Error",None,99,"Critical"]
random.shuffle(raw_logs)
code_1 ="NOMAL"
code_2 ="WARWING"
code_3 ="CRITICAL"
code_4 ="CHECK"
code_5 ="DATAERROR"
code_0 ="EMERGENCY"
print("--실시간 보안 점검 시스템--")
for log in raw_logs:
    try:   
        float(log)
        if log >=99:
            print(f"[{code_0}] 사용률 {log:.1f}% 감지! 해킹 위험 즉시 중단")
            break
        elif log >=90:
            print(f"[{code_3}] 사용률 {log:.1f}%: 즉시 서비스 차단 및 분리")
        elif log >=70:
            print(f"[{code_2}] 사용률 {log:.1f}%: 관리자 호출 및 리소스 확장")
        elif log ==0:
            print(f"[{code_4}] 사용률 {log:.1f}%: 장비 응답 없음 (확인요망)")
        else :
            print(f"[{code_1}] 사용률 {log:.1f}%: 시스템 안정")
    except ValueError:
        print(f"[{code_5}] 읽을 수 없는 로그 형식입니다.(입력값:{log})")
        continue
    except TypeError:
        print(f"[{code_5}] 읽을 수 없는 로그 형식입니다.(입력값:{log})")
        continue    
    except Exception as e:
        print(f"{e} 알수없는 오류 발생")
        break
    finally :
        print("----------점검완료----------")