from typing import Dict, Any
import xml.etree.ElementTree as ET
import xmltodict
import json
import requests
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import JsonOutputParser

def soilexam(service_key, PNU_Code):
    url = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/getSoilExam' # 서비스 URL
    params ={'serviceKey' : service_key, 'PNU_Code' : PNU_Code } #api key와 조회할 토지 주소(법정코드 PNU code)
    response = requests.get(url, params=params) # URL에서 응답 획득.

    response_context = response.text # 응답을 텍스트로 변환. 
    #### xml을 dict 형태로 파싱.
    response_json = xmltodict.parse(response_context)["response"] #xml을 
    # 오류 처리용 분기 처리. 
    try : # 조회 성공시 body 영역의 items내부의 item 데이터만 할당. 
        exam_data = response_json["body"]["items"]["item"]
        return exam_data
    except KeyError: #조회 실패시 0 반환. 
        return 0


def print_recommendations(data):
    # 조회된 토양정보가 없는 경우. 
    if data == 0:
        fail_message = "조회된 토양정보가 없습니다."
        return fail_message
    
    """추천 작물 목록을 출력하는 독립적인 함수"""
    print("=" * 80)
    print("📢 제공된 토양 정보를 기반으로 추천된 작물 목록입니다.")
    print("=" * 80, "\n")

    for idx, rec in enumerate(data["recommendations"], 1):
        if rec['crop'] == "Nan": #작물 이름이 없는 경우. 해당 항목 건너뜀.  
            continue 
        print(f"🌱 추천 작물 {idx}: {rec['crop']}")
        print("-" * 50)
        print("✅ **적정 환경 조건**")
        for key, value in rec["optimal_conditions"].items():
            print(f"  🔹 {key}: {value}")
        print("\n📝 **추천 이유**:")
        print(f"  {rec['reason']}")
        print("=" * 80, "\n")

# 선택한 작물의 정보만 출력하는 함수. 
def get_crop_info(recommendation, crop_name):
    for rec in recommendation["recommendations"]:
        if rec["crop"] == crop_name:
            return rec

class SoilExamRAG:
    def __init__(self, service_key: str, PNU_Code: str, prompt, persist_dir="my_vector_store"):
        """초기화: 모델, 벡터스토어, 프롬프트 템플릿 설정"""
        self.service_key = service_key
        self.PNU_Code = PNU_Code
        self.prompt = prompt

        # OpenAI 모델 설정
        self.model = ChatOpenAI(model="gpt-4o-mini")

        # 벡터 저장소 설정
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=persist_dir, 
            embedding_function=self.embeddings,
        )
        self.retriever = self.vector_store.as_retriever()   
       
    def fetch_soil_data(self) -> Dict[str, Any]:
        """토양 데이터를 API에서 가져오는 함수"""
        return soilexam(self.service_key, self.PNU_Code)  # API 호출

    def retrieve_context(self, input_data: Dict[str, Any]) -> str:
        """입력 데이터를 기반으로 벡터스토어에서 유사 문서 검색"""
        query = "\n".join([f"{key}: {value}" for key, value in input_data.items()]) # dict를 문자열(쿼리)로 변환하는 함수. 
        docs = self.retriever.invoke(query)
        return "\n".join([doc.page_content for doc in docs])

    def get_recommendation(self) -> str:
        """토양 정보를 기반으로 가장 적합한 작물을 추천"""
        input_data = self.fetch_soil_data() # 토양정보 획득. 
        if input_data == 0: #획득한 토양 정보가 없는 경우 0을 반환
            print("조회된 토양 정보가 없습니다.")
            return 0
        
        context = self.retrieve_context(input_data)  # 유사 문서 검색
        parser = JsonOutputParser() #출력을 Json 형태로 처리. 

        # 체인 실행
        chain = self.prompt | self.model | parser
        response = chain.invoke({"input_data": input_data, "context": context})
        return response  
    
# 입력값 지정. 서비스 키 + PNU code
service_key="q+kAKJCJgJXlNlBFxk5LHCmDivqtHEVdmd3vh4cftkCafbEmv4agKxoZemYjbqE9Gxjy0lRCVmbcG3ZtR4K2Tw=="
PNU_Code ='5115034022100750001' # 추후 api 연결하여 자동으로 받아오는 구조로 변경. 

# 프롬프트. 토양정보 받아서 rag 사용하여 적정 환경에 포함되는 작물 추천. 
prompt = PromptTemplate(
    template="""
    아래의 토양 환경 정보를 기반으로 사용자 입력과 비교하여 적합한 작물을 3종류 JSON 형식으로 추천해 주세요.
    JSON에 입력할 값이 없는 경우 Nan을 입력해 주세요. 단. crop 에는 Nan을 입력하면 안됩니다.
    추천이유에는 부정적인 말을 사용하지 말고, 추천한 작물이 사용자 입력의 토양정보에 적합한 이유를 설명하세요. 

    🌱 **사용자 입력 (토양 정보)**:
    {input_data}

    📄 **참고 문서 (작물별 적정 환경)**:
    {context}

    JSON 형식:
    {{
        "recommendations": [
            {{
                "crop": "작물",
                "optimal_conditions": {{
                    "pH": "적정 산도 범위",
                    "SELC" : "전기 전도도",
                    "NO3-N" : "질산태질소 범위",
                    "OM": "적정 유기물 함량",
                    "P": "유효인산 범위",
                    "K": "칼륨 범위",
                    "Ca": "칼슘 범위",
                    "Mg": "마그네슘 범위",                  
                    "B" : "붕소"
                }},
                "reason": "추천 이유"
            }},
            ...
        ]
    }}
    """,
    input_variables=["input_data", "context"]
)


rag_system = SoilExamRAG(service_key=service_key, PNU_Code=PNU_Code, prompt = prompt)
recommendation = rag_system.get_recommendation()

