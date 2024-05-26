import os
import ast
import traceback
import constant as env
import pandas as pd
from operator import itemgetter

from google.oauth2 import service_account
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
from vertexai.preview.generative_models import GenerativeModel

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGCHAIN_PROJECT"]="sql_project"


def main():
    """
        # DB의 Context 정보가 어떻게 쓰이는지 알고 싶을떄.
        context = db.get_context()
        print(list(context))
        
        #prompt가 실제로 되는 부분의 로그가 알고 싶을떄.
        generate_query.get_prompts()[0].pretty_print()
        prompt_with_context = generate_query.get_prompts()[0].partial(table_info=context["table_info"])
    
    """
    try:
        db = connet_db()
        llm = build_llm()

        
        # Question: Question here
        # SQLQuery: SQL Query to run
        # SQLResult: Result of the SQLQuery
        # Answer: Final answer here
        prompt_template = PromptTemplate.from_template("""
        Given an input question, first create a syntactically correct BigQuery query to run, specifically tailored for Google Analytics 4 (GA4) data. 
        Look at the results of the query and return the answer. Unless the user specifies a specific number of examples, always limit your query to at most {top_k} results. 
        Order the results by a relevant column to return the most interesting examples in the database.

        Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.       
        Use UNNEST to flatten any nested fields if necessary.
                                                       
        Use the following format:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here

        Only use the following tables:
        {table_info}
                                                       
        Question: {input}                           
                                                       
        """)
        
        prompt_template.format(table_info="", top_k = 3, input= "이벤트 날짜가 20240520인 데이터 갯수를 알려줘")
        
        #https://api.python.langchain.com/en/latest/chains/langchain.chains.sql_database.query.create_sql_query_chain.html
        generate_query = create_sql_query_chain(llm, db, prompt=prompt_template)

        #STEP1 - chain
        query = generate_query.invoke({"question": "웹사이트나 앱에 정의된 특정 사용자 이벤트에 보고 하는 쿼리를 작성해줘"})
        sql_query = query.split('```sql')[1].split('```')[0].strip()
        
        
        #STEP2 - chain
        execute_query = QuerySQLDataBaseTool(db=db)
        # print(execute_query.invoke(sql_query))      
        
        answer_prompt = PromptTemplate.from_template(
            """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

            Question: {question}
            SQL Query: {query}
            SQL Result: {result}
            Answer: """
        )

        rephrase_answer = answer_prompt | llm | StrOutputParser()
        print(rephrase_answer)
        print("rephrase_answer>>>>>>>")
        # chain = (
        #     RunnablePassthrough.assign(query=sql_query).assign(
        #         result=itemgetter("query") | execute_query
        #     )
        #     | rephrase_answer
        # )
        # print(RunnablePassthrough.assign(query=generate_query))
        chain = (
            RunnablePassthrough
            .assign(query=generate_query)
            .assign(result=itemgetter("query") | execute_query)
            | rephrase_answer
        )

        real = chain.invoke({"question": "웹사이트나 앱에 정의된 특정 사용자 이벤트에 보고 하는 쿼리를 작성해줘"})
        print(real)
        
        
    except Exception as e:
        print("main 함수에서 에러 발생: ", e)

def connet_db():
    try:
        print("Connecting to db...")\
        
        ### Bigquery - DB 정보
        #현재는 단일 테이블이라는 가정. 추가 여러 테이블의 들어갈시, 추가 로직이 필요 할듯 함
        data_set = "temp_w_ga4"
        table_name= "events_"
        ###

        #DB 엔진 생성
        engine = create_engine(f'bigquery://{env.project_id}', credentials_path=env.GOOGLE_APPLICATION_CREDENTIALS)

        with engine.connect() as connection:
            table_result = connection.execute(text(f"""SELECT column_name, data_type, is_nullable
                                            FROM `{env.project_id}.{data_set}.INFORMATION_SCHEMA.COLUMNS` 
                                            WHERE table_name = '{table_name}'"""))
            rows_result = connection.execute(text(f'SELECT * FROM `{env.project_id}.{data_set}.{table_name}` LIMIT 3'))
        #connect() close
                                        
        table_info = table_result.fetchall()
        rows = rows_result.fetchall()
        
        data = {
            "column_name": [info[0] for info in table_info],
            "data_type": [info[1] for info in table_info],
            "is_nullable": [info[2] for info in table_info]
        }
        table_schma = pd.DataFrame(data)

        column_names = rows_result.keys()
        rows_str = f'/*\n3 rows from {env.project_id}.{data_set}.{table_name} table:\n'
        if rows:
            rows_str += '\t'.join(column_names) + '\n'
            for row in rows:
                rows_str += '\t'.join(str(value) for value in row) + '\n'
            rows_str += '*/'
        
        table_rows = rows_str

        custom_info = {
            'temp_w_ga4.events_': f"""
            tableName: {env.project_id}.{data_set}.{table_name}
            
            tableSchema: 
            {table_schma}

            {table_rows}
            """
        }

        db = SQLDatabase(engine=engine, include_tables=['temp_w_ga4.events_'], custom_table_info=custom_info)
        
        # print(db.dialect)
        # print(db.get_usable_table_names())
        # print(db.get_table_info())

        return db
        
    except Exception as e:
        raise Exception(f"connet_db 함수에서 에러 발생: {e}")
    
    
def build_llm():
    try:
        print("build_llm...")
        
        credential = service_account.Credentials.from_service_account_file(
            env.GOOGLE_APPLICATION_CREDENTIALS,
            # scopes=['https://www.googleapis.com/auth/bigquery']
            )
        vertexai.init(project=env.project_id, location=env.region, credentials = credential)
                
        llm = VertexAI(
            model_name=env.gemini_1_5_flash,
            max_output_tokens=8092,
            temperature=0.5,
            top_p=1,
            top_k=40,
            verbose=True
        )
        
        return llm
    
    except Exception as e:
        raise Exception(f"build_llm 함수에서 에러 발생:  {e}")