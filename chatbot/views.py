# views.py
from django.http import JsonResponse
from django.shortcuts import render
from .utils import address_info,soilexam,SoilExamRAG

def soil_recommendation_view(request):
    address = request.GET.get('address', '전라남도 해남군 산이면 덕송리 751') # 디폴트 값으로 테스트용 주소 정보 입력, front 연결시 제거 
    type = request.GET.get('type','PARCEL') # 디폴트 값으로 지번주소 조회. 
    if not address:
        return JsonResponse({"error": "주소를 입력해 주세요."}, status=400)
        
    add_info = address_info(type, address)
    if not add_info:
        return JsonResponse({"error": "유효하지 않은 주소입니다."}, status=400)
    
    PNU_Code = add_info["id"]    
    
    rag_system = SoilExamRAG(PNU_Code=PNU_Code)
    recommendation = rag_system.get_recommendation()
    if not recommendation:
        return JsonResponse({"message": "토지 정보를 얻지 못하였습니다."}, status=404)
    
    return JsonResponse({"recommendations": recommendation})
