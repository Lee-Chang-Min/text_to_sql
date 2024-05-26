import sys
import os
import vertexai
from google.cloud import bigquery
from google.oauth2 import service_account
from vertexai.preview.generative_models import GenerativeModel
# from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_vertexai import VertexAI
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

# from langchain_core.prompt_values import PromptValue
# from langchain_core.outputs import LLMResult

# from typing import (
#     List,
#     Optional,
# )
# from langchain_openai import ChatOpenAI
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
# You have access to tools for interacting with the database.
# Only use the given tools. Only use the information returned by the tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

# If the question does not seem related to the database, just return "I don't know" as the answer.



import constant as env
import tableSchma as schma
import fewShot as fewShot
import logging

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="../key.json"
os.environ["GOOGLE_API_KEY"] = 'AIzaSyDzSNI1-BkbeIe6g-6aj_iUvBdoIS-1000'


logging.basicConfig(
  format = '%(asctime)s:%(levelname)s:%(message)s',
  #datefmt = '%Y-%m-%d: %I:%M:%S %p',
  level = logging.INFO
)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

service_account_file = env.GOOGLE_APPLICATION_CREDENTIALS
credential = service_account.Credentials.from_service_account_file(
    service_account_file,
    # scopes=['https://www.googleapis.com/auth/bigquery']
    )

# vertexai.init(project=env.project_id, location=env.region, credentials = service_account_file)


def googleOauth2():
    credential = service_account.Credentials.from_service_account_file(
        service_account_file,
        # scopes=['https://www.googleapis.com/auth/bigquery']
        )
    
    # credential: credential이 존재하지 않으면 True, 존재하면 False를 반환합니다.
    # credential.valid: credential이 유효하면 True, 유효하지 않으면 False를 반환합니다.
    if not credential or credential.valid:
        print('Unable to authenticate using service account key.')
        sys.exit()
    return credential

                
def connect_to_bigquery():
    try:
        print("Connecting to client...")
        # project_id = googleOauth2().project_id # project_id is stored in the credentials
        
        engine = create_engine(f'bigquery://{env.project_id}', credentials_path=service_account_file)
        # db = SQLDatabase(engine=engine, include_tables=['temp_w_ga4.02_page_brand'])
        db = SQLDatabase(engine=engine, include_tables=['temp_w_ga4.events_'])
        
        # SQL_ALCHEMY_URL = f'bigquery://{env.project_id}//temp_w_ga4?credentials_path={service_account_file}'
        # db = SQLDatabase.from_uri(SQL_ALCHEMY_URL)
        
        
        print("Database dialect:", db.dialect)
        print("Usable table names:", db.get_usable_table_names())
        
        result = db.run("SELECT * FROM `temp_w_ga4.events_`LIMIT 3;")
        print("Query results:", result)
    
        vertexai.init(project=env.project_id, location=env.region, credentials = credential)
            
        llm = VertexAI(
            model_name="gemini-1.5-pro-preview-0514",
            # model_name="gemini-pro",
            max_output_tokens=8092,
            temperature=0.5,
            top_p=1,
            top_k=40,
            verbose=True
        )
        
        
        toolkit = SQLDatabaseToolkit(db=db, llm=llm) 
        
        # example_selector = SemanticSimilarityExampleSelector.from_examples(
        #     # examples,
        #     # https://cloud.google.com/blog/products/ai-machine-learning/google-cloud-announces-new-text-embedding-models?hl=en
        #     GoogleGenerativeAIEmbeddings(model=env.text_embedding_model),
        #     FAISS, # 벡터 검색을 위한 저장소
        #     k=5,
        #     input_keys=["input"], # 입력 텍스트 키를 지정.
        # )
        prefix = """ You are an agent designed to interact with a SQL database.
            Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
            Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
            answer all action and thought in Korean and the final answer in Korean

        """
        
        agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, prefix=prefix, verbose=True)
        # print(agent_executor)
        prompt = PromptTemplate.from_template("""

                                              
            """)
        response = agent_executor.invoke(
            {
                "input": f" 테이블 이름은 temp_w_ga4.events_이고 event_date가 '20240520' 인것과 mobile_brand_name이 'Samsung' 데이터들을 보여줘, 그리고 테이블에 대한 스키마는 {schma.event_table_info} 이 정보를 참고해줘. 최대 보여주는 열의 갯수는 5개로 제한해."
            }
        )
        
        print(response)
        
    except Exception as e:
        print("connet_to_bigquery 함수에서 에러 발생: ", str(e))
        
        
    
def call_gemini(prompt, gemini_model):
    
    # gemini_model = GenerativeModel(gemini_model)
    gemini_model = GenerativeModel(env.gemini_1_5_flash)

    generation_config = {
        "max_output_tokens": 8092,
        "temperature": 0.5,
        "top_p": 0.95,
    }
    responses = gemini_model.generate_content(
        [prompt],
        generation_config = generation_config
    ) 

    logging.debug(f"[Controller][call_gemini] Final response Len {(responses.text)}")

    return responses.text        