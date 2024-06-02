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


                Output: ["fixed_query"]
                
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

