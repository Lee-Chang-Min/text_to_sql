dryRunPrompt= """
                당신은 GA4 BigQuery 전문가입니다. 당신의 임무는 오류 메시지와 쿼리를 분석하여 문제를 식별하고 수정된 쿼리 버전을 제공하는 것입니다.
                답변 형태는 반드시 수정된 쿼리문 만 반환해주세요.

                테이블 명: `{tableName}`
                            
                Input:
                1. 오류 메시지: {error_message}
                2. SQL 쿼리: {sql_query}

                Instructions:
                1. Record 유형의 필드가 있는 컬럼을 참고하여 쿼리를 작성 할 경우 UNNEST 문법 사용해주세요.
                2. Analyze the provided error message to understand the specific issue with the SQL query.
                3. Identify the exact part of the SQL query that is causing the error.
                4. Rewrite the SQL query to correct the error.
                5. Ensure the corrected query follows the syntax and constraints of BigQuery.


                Output the final SQL query only.
                
            """

createQeuryPrompt = """
                Given an input question, first create a syntactically correct BigQuery query to run, specifically tailored for Google Analytics 4 (GA4) data. 
                Look at the results of the query and return the answer. Unless the user specifies a specific number of examples, always limit your query to at most {top_k} results. 
                Order the results by a relevant column to return the most interesting examples in the database. When writing a query referencing a router with fields of record type, please use the UNNEST method.

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
                                                            
                """

naturalPrompt =  """
                Given the following user question, corresponding SQL query, and SQL result, answer the user question in the same language as the question.

                Question: {question}
                SQL Query: {query}
                SQL Result: {result}
                Answer: 

                """


barPossiblePrompt = """
            당신은 <query>가 실행된 <data>의 내용을 바탕으로 
            막대 그래프 차트를 표현 할 수 있는 데이터 인지 판단하는 AI Agent 입니다.
            
            <query>{query}</query>
            <data>{data}</data>

            막대 그래프는 각 항목에 해당하는 수치를 나타내는 막대로 표현할 수 있어야 합니다.
            각 데이터의 항목은 튜플 형태로 구성되어 있습니다. 이 데이터를 사용하여 막대 그래프를 그릴 수 있는지 판단하세요. 
            막대 그래프로 표현 할 수 있으면 "Y" 표현 할 수 없으면 "N" 로 답하세요.

            Output: only "Y" or "N" (no additional characters or spaces)
            """

barChartPrompt = """
                
                당신은 Streamlit 의 altair 라이브러리를 통해 bar chart를 개발하는 AI 에이전트 입니다.
                <data>를 분석하여 "x축", "y축", "color", "tooltip", "title" 5가지를 정해주세요.

                <data>{data}</data>

                example code:'''
                alt.Chart(data_df).mark_bar().encode(
                x='device_category:N',
                y='session_count:Q',
                color='device_category:N',
                tooltip=['device_category', 'session_count']).properties(title='Device Category vs. Session Count', width=600)
                '''

                답변 포맷: {"x": x축, "y": y축, "color": color, "tooltip":tooltip, "title": title}

                """