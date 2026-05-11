import requests
from bs4 import BeautifulSoup
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def get_news():
    try:                                                            
        url = 'https://boannews.com/media/list.asp'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)  
        response.raise_for_status()                                 

        soup = BeautifulSoup(response.text, 'html.parser')
        result = []
        new_list = soup.select(".news_list")

        for news in new_list[:5]:
            title  = news.select_one(".news_txt").get_text(strip=True)
            content = news.select_one(".news_content").get_text(strip=True)
            writer = news.select_one(".news_writer").get_text(strip=True)
            link   = "https://boannews.com" + news.find('a')["href"]
            result.append({"title": title, "content": content, "writer": writer, "link": link})

        return result

    except Exception as e:
        print(f"[스크래핑 오류] {e}")
        return []                                                  


def send_boan_news(news_list):
    user_email    = os.getenv("EMAIL_USER")
    user_password = os.getenv("EMAIL_PASS")
    smtp_server   = os.getenv("SMTP_SVR")
    smtp_port     = int(os.getenv("SMTP_PORT"))

    msg = MIMEMultipart()
    msg['Subject'] = "[최신 뉴스 전달] 실시간 보안 뉴스"
    msg['From'] = user_email
    msg['To']   = user_email

   
    rows = ''.join([
        f"""
        <tr>
            <td style="background:#ffffff; padding:20px; border-radius:10px;
                       box-shadow:0 2px 6px rgba(0,0,0,0.08); margin-bottom:10px;">
                <a href="{news['link']}" style="font-size:16px; font-weight:bold;
                   color:#2980b9; text-decoration:none;">
                    {news['title']}
                </a>
                <div style="font-size:13px; color:#888; margin-top:6px;">
                    ✍️ {news['writer'][:7]}
                </div>
            </td>
        </tr>
        <tr><td height="10"></td></tr>
        """
        for news in news_list
    ])

    html_content = f"""
        <div style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:20px;">
            <h2 style="text-align:center; color:#333;">🔐 보안 뉴스 브리핑</h2>
            <p style="text-align:center; color:#777; font-size:14px;">
                최신 보안 이슈를 한눈에 확인하세요
            </p>
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="max-width:600px; margin:0 auto;">
                {rows}
            </table>
            <p style="text-align:center; font-size:12px; color:#aaa; margin-top:20px;">
                © 2026 Security News Digest
            </p>
        </div>
    """

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(user_email, user_password)
            server.send_message(msg)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 메일 발송 성공")
    except Exception as e:
        print(f"[이메일 오류] {e}")


def daily_work():                                                   
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 작업 시작...")
    news_list = get_news()

    if len(news_list) < 5:
        print(f"  ⚠️ 수집된 기사 수 부족: {len(news_list)}개")

    send_boan_news(news_list)


if __name__ == "__main__":
    print("스케줄러가 동작됩니다. 종료하시려면 Ctrl + C")

    daily_work()                                                    
    schedule.every(1).minutes.do(daily_work)                       

    while True:
        schedule.run_pending()
        time.sleep(1)