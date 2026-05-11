from ftplib import FTP
import os
import re
import openpyxl
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time
import shutil
LOG_PATTERN = re.compile(
    r'(\d+\.\d+\.\d+\.\d+)'        # 그룹1: IP 주소
    r'\s+-\s+-\s+'                   # 구분자 (- -)
    r'\[(.+?)\]'                     # 그룹2: 시간 [01/May/2026:00:02:11 +0900]
    r'\s+"(.+?)"'                    # 그룹3: 요청 내용 "GET / HTTP/1.1"
    r'\s+(\d{3})'                    # 그룹4: 상태 코드 (3자리)
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def analyze_log(log_path='access.log'):
    """
    [가이드 1] 로그 파일 분석
    - 각 라인을 정규식으로 파싱
    - 400 이상 상태코드만 필터링
    - 형식 안 맞는 라인은 continue로 건너뜀
    """
    error_records = []

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # [가이드 1-3] re.search() 결과가 None이면 continue
            match = LOG_PATTERN.search(line)
            if match is None:
                print(f"[무시] 형식 불일치: {line[:50]}")
                continue

            ip     = match.group(1)           # IP 주소
            time_  = match.group(2)           # 시간
            req    = match.group(3)           # 요청 내용
            status = int(match.group(4))      # [가이드 1-2] int()로 변환

            # [가이드 1-2] 400 이상인 경우만 리스트에 추가
            if status >= 400:
                error_records.append([ip, time_, req, status])
                print(f"[에러 감지] {ip} | {time_} | {status} | {req}")

    print(f"\n총 {len(error_records)}건의 에러 로그 발견\n")
    return error_records



def create_excel(records):
    """
    [가이드 2] 엑셀 동적 생성
    - Workbook() 초기화
    - 첫 행에 헤더 삽입
    - 파일명에 날짜+시(Hour) 포함
    """
    # [가이드 2-1] Workbook 초기화
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "에러 로그"

    # [가이드 2-1] 첫 행에 헤더 삽입
    ws.append(['IP 주소', '발생 시간', '요청 내용', '상태 코드'])

    # 데이터 행 추가
    for record in records:
        ws.append(record)

    # [가이드 2-2] 파일명 동적 할당 - 날짜+시간 포함
    # 예: error_report_20260501_00.xlsx
    now = datetime.now()
    filename = now.strftime("error_report_%Y%m%d_%H.xlsx")

    wb.save(filename)
    print(f"[엑셀 생성 완료] {filename} ({len(records)}행)")
    return filename


def upload_ftp(filename):
    """
    [가이드 3] FTP 업로드
    - .env에서 host/port 읽기
    - FTP 접속 및 로그인
    - /backup 디렉토리로 이동 후 업로드
    """
    load_dotenv()
    host = os.getenv('host')
    port = int(os.getenv('port'))

    print(f"[FTP] 접속 시도 → {host}:{port}")

    # [가이드 3-1] FTP 객체 생성 및 로그인
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login("anonymous", "anonymous")
        print("=== FTP 서버 접속 완료 ===")

        # [가이드 3-2] /backup 디렉토리로 이동 (없으면 생성)
        try:
            ftp.cwd('/backup')
        except Exception:
            ftp.mkd('/backup')
            ftp.cwd('/backup')
        print("[디렉토리] /backup 이동 완료")

        # [가이드 3-3] 바이너리 전송 (데이터 손상 방지)
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
            print(f"[FTP 업로드 완료] {filename} → /backup/{filename}")


# ============================================================
# [요구사항 4] 자동화 스케줄링 및 파일 정리
# ============================================================

def job():
  
    print(f"\n{'='*55}")
    print(f"[작업 시작] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    # 1. 로그 분석
    records = analyze_log(os.path.join(BASE_DIR, 'access.log'))

    if not records:
        print("[알림] 400 이상 에러 로그가 없습니다.")
        return

    # 2. 엑셀 생성
    filename = create_excel(records)

    # 3. FTP 업로드
    upload_ftp(filename)

    # [가이드 4-2] 후처리: 로컬 임시 파일 삭제
    os.remove(filename)
    print(f"[정리 완료] 임시 파일 '{filename}' 삭제됨")
    print(f"{'='*55}\n")


# ============================================================
# 실행 진입점
# ============================================================

if __name__ == "__main__":
    # [가이드 4-1] 매시간 정각(:00)에 자동 실행
    schedule.every().hour.at(":00").do(job)

    print("=== 스케줄러 시작 (매시간 정각 자동 실행) ===")
    print("테스트를 위해 즉시 1회 실행합니다...\n")

    # 즉시 1회 실행 (테스트용)
    job()

    # 스케줄 루프
    while True:
        schedule.run_pending()
        time.sleep(1)