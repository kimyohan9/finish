import requests
from bs4 import BeautifulSoup 
import re
from crawled_data.models import BoardData

def crawl_and_save(cntns_no):
    url = f"https://www.nongsaro.go.kr/portal/ps/psb/psbl/workScheduleDtl.ps?menuId=PS00087&cntntsNo={cntns_no}&sKidofcomdtySeCode=FC01"  # 크롤링할 웹사이트 URL
    
    # 웹 페이지 요청
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # id="contents"인 div 요소 찾기
        contents_div = soup.find("div", id="contents")

        # ✅ floatDiv 안의 h4 태그 값 가져오기
        h4_tag = soup.select_one("div.floatDiv h4")  # floatDiv 내부의 h4 태그 선택
        vegetable_name = h4_tag.text.strip() if h4_tag else "이름 없음"  # 텍스트 추출 및 공백 제거

        # ✅ <script> 태그에서 colSpanVal 값 추출
        script_text = " ".join([script.text for script in soup.find_all("script") if script.text])
        colspan_values = re.findall(r'console\.log\("colSpanVal\s*:\s*"\s*\+\s*"(\d+)"\);', script_text)

        print("📌 추출된 colSpanVal 값:", colspan_values)  # ['4', '4', '3', '5', ...]

        # ✅ <script> 태그 전체를 주석 처리
        for script in soup.find_all("script"):
            commented_script = f"<!-- {script} -->"  # script 태그 전체를 문자열로 변환 후 주석 처리
            script.replace_with(BeautifulSoup(commented_script, "html.parser"))  # 변경된 내용을 적용

        if contents_div:
            # BoardData 모델에 저장
            BoardData.objects.create(tag=str(contents_div), vegetablename=vegetable_name)

            print("🌱 채소 이름:", vegetable_name)  
            print(str(contents_div))
            print("\n✅ 크롤링 및 저장 완료!")
        else:
            print("⚠️ 'contents' ID를 가진 div를 찾을 수 없습니다.")
    else:
        print(f"❌ 페이지 요청 실패: {response.status_code}")

# 실행 테스트
# crawl_and_save('')  # 원하는 인자를 전달해서 실행

















# import requests
# from bs4 import BeautifulSoup 
# import re
# from crawled_data.models import BoardData

# def crawl_and_save(cntns_no):
#     url = f"https://www.nongsaro.go.kr/portal/ps/psb/psbl/workScheduleDtl.ps?menuId=PS00087&cntntsNo={cntns_no}&sKidofcomdtySeCode=FC01"  # 크롤링할 웹사이트 URL
    
#     # 웹 페이지 요청
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         # HTML 파싱
#         soup = BeautifulSoup(response.text, "html.parser")

#         # id="contents"인 div 요소 찾기
#         contents_div = soup.find("div", id="contents")

#         # ✅ <script> 태그에서 colSpanVal 값 추출
#         script_text = " ".join([script.text for script in soup.find_all("script") if script.text])
#         colspan_values = re.findall(r'console\.log\("colSpanVal\s*:\s*"\s*\+\s*"(\d+)"\);', script_text)

#         print("📌 추출된 colSpanVal 값:", colspan_values)  # ['4', '4', '3', '5', ...]

#         # ✅ <script> 태그 전체를 주석 처리
#         for script in soup.find_all("script"):
#             commented_script = f"<!-- {script} -->"  # script 태그 전체를 문자열로 변환 후 주석 처리
#             script.replace_with(BeautifulSoup(commented_script, "html.parser"))  # 변경된 내용을 적용

                
#         if contents_div:
#             # # 기본 HTML 구조에 크롤링한 내용을 포함
#             # html_content = f"""
#             # <!DOCTYPE html>
#             # <html lang="ko">
#             # <head>
#             #     <meta charset="UTF-8">
#             #     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             #     <title>크롤링 데이터</title>
#             # </head>
#             # <body>
#             #     {contents_div}
#             # </body>
#             # </html>
#             # """

#             # # HTML 파일로 저장
#             # with open("crawled_content.html", "w", encoding="utf-8") as file:
#             #     file.write(html_content)
#             BoardData.objects.create(tag=str(contents_div))
#             print(str(contents_div))
#             print("\n:흰색_확인_표시: 크롤링 및 저장 완료!")
#             print("✅ HTML 파일 저장 완료! (crawled_content.html)")
#         else:
#             print("⚠️ 'contents' ID를 가진 div를 찾을 수 없습니다.")
#     else:
#         print(f"❌ 페이지 요청 실패: {response.status_code}")

# # 실행 테스트
# # crawl_and_save('')  # 원하는 인자를 전달해서 실행
