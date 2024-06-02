import os
import ast
import constant as env
import customPrompt
import pandas as pd
from operator import itemgetter

from google.auth import default
from google.oauth2 import service_account
from google.cloud import bigquery
from langsmith import traceable

from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.chains.sql_database.query import create_sql_query_chain

from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, QuerySQLCheckerTool
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.runnables import RunnablePassthrough 

import vertexai
from langchain_google_vertexai import VertexAI
from vertexai.generative_models import GenerativeModel

import logging
import debugpy
import coloredlogs

#devcontainer debug
# debugpy.listen(("0.0.0.0", 5678))
# print("Waiting for debugger attach...")

logging.basicConfig(
  format = '%(asctime)s:%(levelname)s:%(message)s',
  #datefmt = '%Y-%m-%d: %I:%M:%S %p',
  level = logging.INFO
)
#INFO 레벨도 logging 하기 위한 옵션
logging.getLogger().setLevel(logging.INFO)


class SqlController():

    """
    NLP to SQL 처리 클래스 
    
        1.

    """
    credentials = None

    bigquery_client = None
    db_client = None
    llm_client = None

    project_id = env.project_id
    region = env.region

    data_set = "temp_w_ga4"
    table_name= "events_"

    def __init__(self, prod:bool):

        # if prod = False, use local file key.json
        if not prod:

            #langsmith 연동 부분
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"]="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"
            os.environ["LANGCHAIN_PROJECT"]="sql_project"

        
            # the location of service account in Cloud Shell.
            SqlController.credentials = service_account.Credentials.from_service_account_file(
                env.service_acc_localFile, 
                # scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
          
        else:
            # Use default auth in Cloud Run env. 
            SqlController.credentials, _ = default()
            
        logging.info(f"[SQLController][__init__] SQLController.credentials  : {SqlController.credentials}")

        # Initialize Vertex AI env with the credentials. 
        vertexai.init(project=env.project_id, location=env.region, credentials = SqlController.credentials)
        #Biqeury Client
        SqlController.bigquery_client = bigquery.Client(credentials=SqlController.credentials) 
        logging.info(f"[SQLController][__init__] SQLController  : vertaxai init => success, bigqueryclient => success")

        #connect_db
        SqlController.db_client = self.connect_db(SqlController.data_set, SqlController.table_name)
        SqlController.llm_client = self.vertax_llm(env.gemini_1_5_flash)
        logging.info(f"[SQLController][__init__] Initialize SQLController done!")
        

    def response(self, question:str):
        """
            사용자의 질문을 파악하여 sql을 생성한 후 자연어 답변 Flow.
                1.
                2.
                3.    

        
            #DB의 Context 정보가 어떻게 쓰이는지 알고 싶을떄.
            context = db.get_context()
            print(list(context))
            
            #prompt가 실제로 되는 부분의 로그가 알고 싶을떄.
            generate_query.get_prompts()[0].pretty_print()
            prompt_with_context = generate_query.get_prompts()[0].partial(table_info=context["table_info"])
        
        """
        try:
            logging.info(f"[SQLController][response] sql generative start!")
            prompt_template = PromptTemplate.from_template(customPrompt.createQeuryPrompt)
            
            #https://api.python.langchain.com/en/latest/chains/langchain.chains.sql_database.query.create_sql_query_chain.html
            #STEP1 - Create Query Chain
            generate_query = create_sql_query_chain(self.llm_client, self.db_client, prompt=prompt_template)
            # generate_query.get_prompts()[0].pretty_print()        
            query_response = generate_query.invoke({"question": question})  
            logging.info(f"[SQLController][response] Query Response: {query_response}")  

            sql_query = self.extract_sql_query(query_response)
            #쿼리 오류가 없을 시 fix_query = None 
            fix_query = self.dry_run(sql_query)    
            final_query = sql_query if fix_query is None else fix_query

            
            #STEP2 - 자연어 처리 chain
            execute_query = QuerySQLDataBaseTool(db=self.db_client)
            answer_prompt = PromptTemplate.from_template(customPrompt.naturalPrompt)

            rephrase_answer = answer_prompt | self.llm_client | StrOutputParser()

            chain = RunnablePassthrough.assign(
                query=lambda _: {"query": final_query}
            ).assign(
                result=itemgetter("query") | execute_query
            ) | rephrase_answer
            
            result = chain.invoke({"question": question})

            logging.info(f"[SQLController][response] final responses : {result}")

            return f"실행된 쿼리: {final_query}\n\n답변: {result}"        
            
        except Exception as e:
            logging.error(f"[SQLController][response] response function Error : {e}")


    def connect_db(self, data_set:str, table_name:str):
        """
        langchain SQLDatabase setting 
        custom table info setting
        """
        try:
            #DB 엔진 생성
            engine = create_engine(f'bigquery://{self.project_id}', credentials_path=env.service_acc_prod)

            with engine.connect() as connection:
                table_result = connection.execute(text(f"""SELECT column_name, data_type, is_nullable
                                                FROM `{self.project_id}.{data_set}.INFORMATION_SCHEMA.COLUMNS` 
                                                WHERE table_name = '{table_name}'"""))
                rows_result = connection.execute(text(f'SELECT * FROM `{self.project_id}.{data_set}.{table_name}` LIMIT 3'))

                                            
            table_info = table_result.fetchall()
            rows = rows_result.fetchall()
            
            data = {
                "column_name": [info[0] for info in table_info],
                "data_type": [info[1] for info in table_info],
                "is_nullable": [info[2] for info in table_info]
            }
            table_schma = pd.DataFrame(data)

            column_names = rows_result.keys()
            rows_str = f'/*\n3 rows from {self.project_id}.{data_set}.{table_name} table:\n'
            if rows:
                rows_str += '\t'.join(column_names) + '\n'
                for row in rows:
                    rows_str += '\t'.join(str(value) for value in row) + '\n'
                rows_str += '*/'
            
            table_rows = rows_str

            custom_info = {
                f'{data_set}.{table_name}': f"""
                tableName: {self.project_id}.{data_set}.{table_name}
                
                tableSchema: 
                {table_schma}

                {table_rows}
                """
            }

            db = SQLDatabase(engine=engine, include_tables=[f'{data_set}.{table_name}'], custom_table_info=custom_info)
            # logging.info(custom_info)
            logging.info(f"[SQLController][connect_db] connect db complete!")
            # print(db.dialect)
            # print(db.get_usable_table_names())
            # print(db.get_table_info())

            return db
            
        except Exception as e:
            logging.error(f"[SQLController][connect_db] : {e}")

    def vertax_llm(self, gemini_model:str):
        """
        setting vertax ai llm
        """
        try:
            vertax_llm = VertexAI(
                model_name=gemini_model,
                max_output_tokens=8192,
                temperature=0.5,
                top_p=1,
                top_k=40
            )
            logging.info(f"[SQLController][vertax_llm] vertax_llm build complete!")
            return vertax_llm
        
        except Exception as e:
            logging.error(f"[SQLController][vertax_llm]  : {e}")
        
    def generation_llm(self, prompt, gemini_model):
        """
        setting GenerativeModel llm
        """
        try:
            
            generation_config = {
                "max_output_tokens": 8192,
                "temperature": 0.5,
                "top_p": 1,
                "top_k": 40
            }   
            multimodal = GenerativeModel(model_name=gemini_model, generation_config = generation_config)
            responses = multimodal.generate_content([prompt]) 
            logging.debug(f"[SQLController][generation_llm] Final response Len {len(responses.text)}")

            return responses.text
        
        except Exception as e:
            logging.error(f"[SQLController][generation_llm]  : {e}")

    def dry_run(self, sql_query: str):
        """
        dry run 으로 쿼리 확인 후 오류 발생 시 쿼리 수정 요청
        """
        try:   
            # Dry run 설정
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

            query_job = self.bigquery_client.query(sql_query, job_config=job_config)
                
            # dry run
            if query_job.errors:
                error_message = query_job.errors
                logging.error(f"[SQLController][dry_run] Dry run error occurred: {error_message}")

            # A dry run query completes immediately.
            logging.info("[SQLController][dry_run] : This query will process {} bytes.".format(query_job.total_bytes_processed))
            
            return None
            
        except Exception as e:
            logging.error(f"[SQLController][dry_run]: {e}")
            
            prompt = PromptTemplate.from_template(customPrompt.dryRunPrompt)
            
            final_prompt = prompt.format(tableName= f'{self.data_set}.{self.table_name}',error_message=e, sql_query=sql_query)
            fix_sql = self.generation_llm(final_prompt, env.gemini_1_5_pro)
            logging.info(f"[SQLController][dry_run] 쿼리 수정 : {fix_sql}")
            
            return self.extract_sql_query(fix_sql)
        
        finally:
            logging.info(f"[SQLController][dry_run] dry run complete")

    def extract_sql_query(self, query: str):
        if '```sql' in query:
            return query.split('```sql')[1].split('```')[0].strip()
        elif 'SQLQuery:' in query:
            return query.split('SQLQuery:')[1].strip().split('\n')[0].strip()
        else:
            logging.error(f"[SQLController][extract_sql_query] query를 추출 할 수 없음: queryOutput{query}")
