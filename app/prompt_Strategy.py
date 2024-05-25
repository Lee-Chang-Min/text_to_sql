import os
import constant as env
from google.oauth2 import service_account
from langsmith import traceable

from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain.chains.sql_database.query import create_sql_query_chain

from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, QuerySQLCheckerTool

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
        db = connet_db();
        llm = build_llm();
        context = db.get_context()
        print(list(context))
        prompt_template = PromptTemplate.from_template("""
        Given an input question, first create a syntactically correct BigQuery query to run, specifically tailored for Google Analytics 4 (GA4) data. 
        Look at the results of the query and return the answer. Unless the user specifies a specific number of examples, always limit your query to at most 5 results. 
        Order the results by a relevant column to return the most interesting examples in the database.

        Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.

        Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.       

        Use the following format:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here

        Only use the following tables:
        {table_info}

        Question: {input}
        """)
        
        table_names = db.get_table_names() 
        table_info = f"""
        tableName: { table_names[0] if len(table_names) == 1 else ", ".join(table_names) }
        
        tableSchma:
        """
        
        print(table_info)
        
        
        prompt_template.format(table_info="funny",)
        #https://api.python.langchain.com/en/latest/chains/langchain.chains.sql_database.query.create_sql_query_chain.html
        generate_query = create_sql_query_chain(llm, db)
        generate_query.get_prompts()[0].pretty_print()
        
        #STEP1 - chain
        query = generate_query.invoke({"question": "user_id의 값이 3518854인 데이터가 몇개야?"})
        print("query >>>>>>>>>>>>>>>>>>", query);
        
        
        #STEP2 - chain
        # adsf = QuerySQLCheckerTool()
        excute_query = QuerySQLDataBaseTool(db=db)
        excute_query.invoke(query)        
        
        
        
        
    except Exception as e:
        print("main 함수에서 에러 발생: ", e)

def connet_db():
    try:
        print("Connecting to db...")
        
        engine = create_engine(f'bigquery://{env.project_id}', credentials_path=env.GOOGLE_APPLICATION_CREDENTIALS)
        db = SQLDatabase(engine=engine, include_tables=['temp_w_ga4.flat_event_params','temp_w_ga4.flat_events', 'temp_w_ga4.flat_items', 'temp_w_ga4.flat_user_properties'])
        
        print(db.dialect)
        print(db.get_usable_table_names())
        # print(db.get_table_info()) #UNNEST는 에러
        
        # INFORMATION_SCHEMA를 통해 table_info 확인
        query = """
        SELECT column_name, data_type, is_nullable
        FROM `lottecard-test.temp_w_ga4.INFORMATION_SCHEMA.COLUMNS` 
        WHERE table_name = 'events_'
        """
        # table_info = db.run(query)
        # print("테이블 정보:", table_info)
        
        # result = db.run("SELECT * FROM `temp_w_ga4.events_`LIMIT 3;")
        # print("Query results:", result)
        
        return db;
        
    except Exception as e:
        print("connet_db 함수에서 에러 발생: ", str(e))
    
    
def build_llm():
    try:
        print("build_llm...")
        
        credential = service_account.Credentials.from_service_account_file(
            env.GOOGLE_APPLICATION_CREDENTIALS,
            # scopes=['https://www.googleapis.com/auth/bigquery']
            )
        vertexai.init(project=env.project_id, location=env.region, credentials = credential)
                
        llm = VertexAI(
            model_name="gemini-1.5-pro-preview-0514",
            max_output_tokens=8092,
            temperature=0.5,
            top_p=1,
            top_k=40,
            verbose=True
        )
        
        return llm;
    
    except Exception as e:
        print("build_llm 함수에서 에러 발생: ", str(e))
