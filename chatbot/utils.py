import json
import requests  # requests 모듈 추가
import xmltodict
import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv



def address_info(category: str, address: str):
    """주소 정보를 가져오는 함수"""
    if category not in {"ROAD", "PARCEL"}:
        return None  # JsonResponse 대신 None 반환
    load_dotenv()
    vw_key = os.getenv("VWORLD_API_KEY")
    vw_URL = "https://api.vworld.kr/req/search"
    
    params = {'request': "search", 
              'key': vw_key, 
              'query': address, 
              'type': "address", 
              'category': category}
    
    response = requests.get(vw_URL, params=params)
    
    if response.status_code != 200:
        return None
    
    parsed_json = response.json()
    try:
        add_info = parsed_json["response"]["result"]['items'][0]
        return add_info
    except (KeyError, IndexError):
        return None


def soilexam(PNU_Code):
    """토양 정보를 가져오는 함수"""
    url = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/getSoilExam'
    load_dotenv()
    service_key = os.getenv("Soilexam_API_KEY")
    params = {'serviceKey': service_key, 'PNU_Code': PNU_Code}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None
    
    try:
        response_json = xmltodict.parse(response.text)["response"]
        return response_json["body"]["items"]["item"]
    except (KeyError, TypeError):
        return None

class SoilExamRAG:
    """토양 정보 기반 추천 시스템"""
    
    def __init__(self, PNU_Code: str, persist_dir="my_vector_store"):

        load_dotenv()
        open_api_key = os.getenv("opneai_API_KEY")
        self.PNU_Code = PNU_Code       
        self.model = ChatOpenAI(model="gpt-4o-mini", api_key=open_api_key)
        self.embeddings = OpenAIEmbeddings(api_key=open_api_key)
        self.vector_store = Chroma(persist_directory=persist_dir, embedding_function=self.embeddings)
        self.retriever = self.vector_store.as_retriever()
    
    def fetch_soil_data(self):
        """토양 데이터 조회"""
        return soilexam(self.PNU_Code)
    
    def retrieve_context(self, input_data):
        """벡터 데이터베이스에서 컨텍스트 검색"""
        if not input_data:
            return ""
        
        query = "\n".join([f"{key}: {value}" for key, value in input_data.items()])
        docs = self.retriever.invoke(query)
        return "\n".join([doc.page_content for doc in docs]) if docs else ""
    
    def get_recommendation(self):
        """토양 정보를 바탕으로 추천 작물 반환"""
        input_data = self.fetch_soil_data()
        if not input_data:
            return None
        
        prompt = PromptTemplate(
                template="""
                    아래의 토양 환경 정보를 기반으로 사용자 입력과 비교하여 적합한 작물을 3종류 JSON 형식으로 추천해 주세요.

                    JSON에 입력할 값이 없는 경우 null을 입력해 주세요. 단 crop 에는 반드시 작물 이름이 입력되야 합니다. 

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
                        "산도(pH)": "적정 산도 범위",
                        "전기 전도도(SELC)" : "전기 전도도",
                        "질산태질소(NO3-N)" : "질산태질소 범위",
                        "유기물(OM)": "적정 유기물 함량",
                        "유효인산(P)": "유효인산 범위",
                        "칼륨(K)": "칼륨 범위",
                        "칼슘(Ca)": "칼슘 범위",
                        "마그네슘(Mg)": "마그네슘 범위",                  
                        "붕소(B)" : "붕소"
                        }},
                "reason": "추천 이유"
            }},
            ...
            ]
            }}
            """,
        input_variables=["input_data", "context"]
        )

        context = self.retrieve_context(input_data)
        parser = JsonOutputParser()
        chain = prompt | self.model | parser
        response = chain.invoke({"input_data": input_data, "context": context})
        
        return response.get("recommendations", [])


# utils.py에서 직접 실행을 방지하기 위한 코드
if __name__ == "__main__":
    print("이 파일은 Django 프로젝트에서 import하여 사용하세요.")