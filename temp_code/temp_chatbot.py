from typing import Dict, Any
import xml.etree.ElementTree as ET
import xmltodict
import json
import requests
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma


def soilexam(service_key, PUN_code):
    url = 'http://apis.data.go.kr/1390802/SoilEnviron/SoilExam/getSoilExam'
    params ={'serviceKey' : service_key, 'PNU_Code' : PUN_code }
    response = requests.get(url, params=params)

    response_context = response.text
    #### parsing to json
    response_json = xmltodict.parse(response_context)["response"]
    exam_data = response_json["body"]["items"]["item"]
    return exam_data

class SoilExamRAG:
    def __init__(self, service_key: str, PUN_code: str, persist_dir="my_vector_store"):
        """초기화: 모델, 벡터스토어, 프롬프트 템플릿 설정"""
        self.service_key = service_key
        self.PUN_code = PUN_code

        # OpenAI 모델 설정
        self.model = ChatOpenAI(model="gpt-4o-mini")

        # 벡터 저장소 설정
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=persist_dir, 
            embedding_function=self.embeddings,
        )
        self.retriever = self.vector_store.as_retriever()
    

        # 프롬프트 템플릿 설정
        self.prompt = PromptTemplate(
            template="""
            아래의 토양 환경 정보를 기준으로 참고문서에서 키울 수 있는 적합한 작물을 3개 추천해 주세요.
            추천할 때 작물의 번호 및 작물별 적정 환경을 같이 출력해 주세요.
            
            🌱 **사용자 입력 (토양 정보)**:
            {input_data}
            
            📄 **참고 문서 (작물별 적정 환경)**:
            {context}
            
            비교 후 가장 적합한 작물을 추천하고, 그 이유도 설명해 주세요.
            """,
            input_variables=["input_data", "context"]
        )

    def fetch_soil_data(self) -> Dict[str, Any]:
        """토양 데이터를 API에서 가져오는 함수"""
        return soilexam(self.service_key, self.PUN_code)  # API 호출

    def retrieve_context(self, input_data: Dict[str, Any]) -> str:
        """입력 데이터를 기반으로 벡터스토어에서 유사 문서 검색"""
        query = "\n".join([f"{key}: {value}" for key, value in input_data.items()])
        docs = self.retriever.invoke(query)
        return "\n".join([doc.page_content for doc in docs])

    def get_recommendation(self) -> str:
        """토양 정보를 기반으로 가장 적합한 작물을 추천"""
        input_data = self.fetch_soil_data()
        context = self.retrieve_context(input_data)  # 유사 문서 검색

        # 체인 실행
        chain = self.prompt | self.model
        response = chain.invoke({"input_data": input_data, "context": context})
        return response

# 🔹 객체 생성 및 실행
# 입력값 지정. 
service_key="q+kAKJCJgJXlNlBFxk5LHCmDivqtHEVdmd3vh4cftkCafbEmv4agKxoZemYjbqE9Gxjy0lRCVmbcG3ZtR4K2Tw=="
PUN_code ='5115034022100750001' # 추후 api 연결하여 자동으로 받아오는 구조로 변경. 

rag_system = SoilExamRAG(service_key=service_key, PUN_code=PUN_code)
recommendation = rag_system.get_recommendation()
recommendation.pretty_print()
