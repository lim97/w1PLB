import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_KEY")
DB_ID = os.getenv("DATABASE_ID")

if not NOTION_TOKEN or not DB_ID:
    raise ValueError(".env 값 없음")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 수량 정규표현식 검증
def validate_number(value):
    return re.match(r"^\d+$", value) is not None

# 인덱스 선택 검증
def validate_index(max_len):
    value = input("번호 선택: ")
    try:
        idx = int(value)
        if idx < 0 or idx >= max_len:
            print(" 범위 밖입니다")
            return None
        return idx
    except:
        print(" 숫자를 입력하세요")
        return None


# 조회
def get_items():
    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"

    try:
        res = requests.post(url, headers=headers)
        res.raise_for_status()

        results = res.json().get("results", [])

        items = []
        for page in results:
            props = page.get("properties", {})

            title = props.get("상품명", {}).get("title", [])
            name = title[0]["plain_text"] if title else "이름없음"

            qty = props.get("수량", {}).get("number", 0)

            items.append((page["id"], name, qty))

        return items

    except requests.exceptions.HTTPError as e:
        print(f" API 에러: {e}")
        return []
    except Exception as e:
        print(f" 알 수 없는 에러: {e}")
        return []

# 생성
def create_item(name, qty):
    url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": DB_ID},
        "properties": {
            "상품명": {
                "title": [{"text": {"content": name}}]
            },
            "수량": {
                "number": int(qty)
            }
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        print(" 등록 완료")
    except requests.exceptions.HTTPError as e:
        print(f" API 에러: {e}")
    except Exception as e:
        print(f" 알 수 없는 에러: {e}")

# 수정
def update_item(page_id, qty):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {
        "properties": {
            "수량": {
                "number": int(qty)
            }
        }
    }

    try:
        res = requests.patch(url, headers=headers, json=payload)
        res.raise_for_status()
        print(" 수정 완료")
    except requests.exceptions.HTTPError as e:
        print(f" API 에러: {e}")
    except Exception as e:
        print(f" 알 수 없는 에러: {e}")

# 삭제
def delete_item(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"archived": True}

    try:
        res = requests.patch(url, headers=headers, json=payload)
        res.raise_for_status()
        print(" 삭제 완료")
    except requests.exceptions.HTTPError as e:
        print(f" API 에러: {e}")
    except Exception as e:
        print(f" 알 수 없는 에러: {e}")

#프린트 
def print_menu():
    print("\n===== 재고 관리 =====")
    print("1. 전체 조회")
    print("2. 상품 등록")
    print("3. 수량 수정")
    print("4. 상품 삭제")
    print("0. 종료")
# 루프
while True:
    print_menu()
    choice = input("번호를 입력하세요: ")

    # 종료
    if choice == "0":
        print("프로그램 종료")
        break

    # 조회
    elif choice == "1":
        items = get_items()

        if not items:
            print(" 데이터 없음")
            continue

        for i, (_, name, qty) in enumerate(items):
            print(f"{i}. {name} - {qty}")

    # 생성
    elif choice == "2":
        name = input("상품명: ")
        qty = input("수량: ")

        if not validate_number(qty):
            print(" 숫자만 입력하세요")
            continue

        create_item(name, qty)

    # 수정
    elif choice == "3":
        items = get_items()

        if not items:
            print(" 수정할 데이터 없음")
            continue

        for i, (_, name, qty) in enumerate(items):
            print(f"{i}. {name} - {qty}")

        idx = validate_index(len(items))
        if idx is None:
            continue

        qty = input("새 수량: ")
        if not validate_number(qty):
            print(" 숫자만 입력하세요")
            continue

        update_item(items[idx][0], qty)

    # 삭제
    elif choice == "4":
        items = get_items()

        if not items:
            print(" 삭제할 데이터 없음")
            continue

        for i, (_, name, qty) in enumerate(items):
            print(f"{i}. {name} - {qty}")

        idx = validate_index(len(items))
        if idx is None:
            continue

        confirm = input("정말 삭제하시겠습니까? (y/n): ")
        if confirm == "y":
            delete_item(items[idx][0])
        else:
            print("취소됨")
            continue

    else:
        print(" 잘못된 입력")