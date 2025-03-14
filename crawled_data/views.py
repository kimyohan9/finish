import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .crawl import crawl_and_save

@csrf_exempt  # CSRF 방지 (테스트 시 필요, 보안상 주의)
def fetch_and_store(request):
    if request.method == "POST":
        try:
            # 요청 body에서 JSON 데이터 추출
            data = json.loads(request.body.decode("utf-8"))
            cntns_no = data.get("cntns_no")  # 'cntns_no' 키로 값 가져오기
            
            if not cntns_no:
                return JsonResponse({"error": "cntns_no 값이 필요합니다."}, status=400)

            # 크롤링 실행
            crawl_and_save(cntns_no)
            return JsonResponse({"message": "크롤링 및 저장 완료!", "cntns_no": cntns_no})
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "유효한 JSON 형식이 아닙니다."}, status=400)
    
    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)
