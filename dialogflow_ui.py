from google.oauth2 import service_account
# from google.cloud import dialogflowcx_v3 as dialogflow
import streamlit as st
import pandas as pd
import altair as alt
import uuid

import os
import sys
import debugpy

directory = os.getcwd()
sys.path.append(directory+"/src")

from sqlController import SqlController
prod = True

# PROJECT_ID = "lottecard-test"
# LOCATION_ID = "global"
# # SESSION_ID = str(uuid.uuid4())

# LANGUAGE_CODE = "ko"
# # LANGUAGE_CODE = "en"
# CREDENTIALS = service_account.Credentials.from_service_account_file('./key.json')
# client_options = {"api_endpoint": f"{LOCATION_ID}-dialogflow.googleapis.com"}
# AGENT_ID = "2b0a77e3-c4f4-497e-9fe4-b2f36555d95f"

# 임시
# AGENT_ID = "ffbbfee0-8915-49f8-a4c2-702b119b2684"

#CSS
GP_ICON = "https://github.com/Lee-Chang-Min/dialogflow_chatbot/blob/main/images/gpicon.png?raw=true"

# Initialize the Dialogflow session client
# session_client = dialogflow.SessionsClient(client_options=client_options, credentials=CREDENTIALS)


def load_css_from_file():
    with open('css/style.css', "r", encoding='utf-8') as f:
        css_content = f.read()
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

load_css_from_file() 

# UI 구성
with st.sidebar:
    st.image('images/gpside-removebg.png')
    if st.button('+'+'새로운 채팅'):
        st.session_state["messages"] = [{"role": "assistant", "content": "Google Analytics Knowledge base 기반의 Chatbot 서비스 입니다."}]
        st.session_state["session_id"] = str(uuid.uuid4())
    # agent_id = st.text_input("Dialogflow Agent ID", key="dialogflow_agent_id")
    st.markdown("""---""")
    st.text('대화 내역')
    
st.image('images/ga4-removebg.png')
st.title("안녕하세요.")
st.title("무엇을 도와 드릴까요?",)
st.caption("🚀 chatbot powered by Dialogflow CX")

# data = {
#     "unique_users": 366,
#     "unique_events": 19,
#     "unique_dates": 1,
#     "unique_timestamps": 2465,
#     "unique_previous_timestamps": 4,
#     "unique_event_values": 0,
#     "unique_bundle_ids": 3,
#     "unique_server_offsets": 2,
#     "unique_user_ids": 0,
#     "unique_first_touch_timestamps": 365
# }
# # Convert the dictionary to a DataFrame
# data_df = pd.DataFrame(list(data.items()), columns=['Category', 'Values'])
# # data_df = pd.DataFrame({
# #     'Category': ['2020-01-01', '2020-01-02', '2020-01-03'],
# #     'Values': [10, 20, 30]
# # })
# # # Convert data to DataFrame
# chart_type = st.selectbox("차트 유형을 선택하세요:", ('바 차트', '라인 차트', '영역 차트', '점 차트'))

# # 선택된 차트 유형에 따른 차트 렌더링
# if chart_type == '바 차트':
#     chart = alt.Chart(data_df).mark_bar().encode(
#         x='Category:N',
#         y='Values:Q',
#         color='Category:N',
#         tooltip=['Category', 'Values']
#     ).properties(title='Unique Data Metrics', width=600)

# elif chart_type == '라인 차트':
#     chart = alt.Chart(data_df).mark_line().encode(
#         x='Category:N',
#         y='Values:Q',
#         color='Category:N',
#         tooltip=['Category', 'Values']
#     ).properties(title='Unique Data Metrics', width=600)

# elif chart_type == '영역 차트':
#     chart = alt.Chart(data_df).mark_area().encode(
#         x='Category:N',
#         y='Values:Q',
#         color='Category:N',
#         tooltip=['Category', 'Values']
#     ).properties(title='Unique Data Metrics', width=600)

# elif chart_type == '점 차트':
#     chart = alt.Chart(data_df).mark_point().encode(
#         x='Category:N',
#         y='Values:Q',
#         color='Category:N',
#         size='Values:Q',  # 크기를 값에 따라 조절
#         tooltip=['Category', 'Values']
#     ).properties(title='Unique Data Metrics', width=600)

# # Streamlit에 차트 표시
# st.altair_chart(chart, use_container_width=True)

if 'messages' not in st.session_state:
    st.session_state['sqlcontroller'] = SqlController(prod)
    st.session_state["messages"] = [{"role": "assistant", "content": "Google Analytics Knowledge base 기반의 Chatbot 서비스 입니다."}]

sqlcontroller = st.session_state['sqlcontroller']

# if 'session_id' not in st.session_state:
#     st.session_state['session_id'] = str(uuid.uuid4())

for msg in st.session_state.messages:
    if(msg["role"] == 'assistant'):        
        st.chat_message(msg["role"], avatar=GP_ICON).write(msg["content"])
    if(msg["role"] == 'user'):        
        st.chat_message(msg["role"]).write(msg["content"])


# Streamlit chat input
prompt = st.chat_input(placeholder="여기에 메세지를 입력해주세요.")

# def send_to_dialogflow(prompt, AGENT_ID):
#     session_path = session_client.session_path(PROJECT_ID, LOCATION_ID, AGENT_ID, st.session_state["session_id"])
#     text_input = dialogflow.TextInput(text=prompt)
#     query_input = dialogflow.QueryInput(text=text_input, language_code = LANGUAGE_CODE)
    
#     # Send the request to Dialogflow
#     response = session_client.detect_intent(request={"session": session_path, "query_input": query_input})
    
#     # Extract the response message correctly
#     parameters = response.query_result.parameters

#     if parameters == None:
#         return response.query_result.response_messages[0].text.text[0]
#     elif(parameters.get("$request.generative.DynamicFAQResponse") != None):
#         return parameters.get("$request.generative.DynamicFAQResponse")
#     else:
#         return response.query_result.response_messages[0].text.text[0]
    
    # if(AGENT_ID == 'ffbbfee0-8915-49f8-a4c2-702b119b2684'):
    #     # if(response.query_result.parameters != None):
    #     #     return response.query_result.parameters.response_messages[0].text.text[0]
    #     # else:
    #         return response.query_result.response_messages[0].text.text[0]
        
                
if prompt:
    # if not AGENT_ID:
    #     st.info("Please add your Agent Id to continue.")
    #     st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send the user's message to Dialogflow and get the response
    # print(st.session_state['session_id'])
    msg = sqlcontroller.response(prompt)
    
    if msg:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant", avatar=GP_ICON).write(msg)
       
        
        
        
        
        
        
        
        
        
        
# def get_image_base64():
#     with open('./1.png', "rb") as image_file:
#     encoded_string = base64.b64encode(image_file.read()).decode()
#     return f"data:image/png;base64,{encoded_string}"

# msg1 = '''
#         나이키의 검색 광고 캠페인 데이터를 분석한 결과, "운동화" 키워드가 가장 성과가 좋은 것으로 나타났습니다. 이 키워드는 높은 클릭수, 노출수, 비용을 기록했습니다.
 
#  운동화 키워드의 성과 분석
#  높은 클릭률: 4.42%의 클릭률은 업계 평균보다 상당히 높습니다. 이는 나이키가 운동화를 찾는 관련성 있는 청중에게 효과적으로 도달하고 있음을 시사합니다.
#  높은 노출수: 73875회의 노출수는 나이키가 광범위한 잠재 고객에게 노출되고 있음을 보여줍니다.
#  높은 비용: 1,577,385원의 비용은 나이키가 이 키워드에 상당한 투자를 하고 있음을 나타냅니다. 그러나 높은 클릭률과 노출수를 고려하면 이 투자는 가치가 있습니다.
#  적절한 평균 클릭 비용: 482.68원의 평균 클릭 비용은 업계 평균에 부합합니다. 이는 나이키가 경쟁력 있는 가격으로 관련성 있는 트래픽을 확보하고 있음을 시사합니다.
#  추천 검색 광고 캠페인의 성과
#  추천 검색 광고 캠페인에서도 "운동화" 키워드가 가장 성과가 좋았습니다. 이 키워드는 검색 광고 캠페인과 유사한 클릭률, 노출수, 비용을 기록했습니다. 이는 나이키가 추천 검색 광고를 통해 운동화를 찾는 청중에게 효과적으로 도달하고 있음을 시사합니다.
 
# 나이키의 검색 광고 캠페인 데이터 분석 결과, "운동화" 키워드가 가장 성과가 좋은 것으로 나타났습니다. 이 키워드는 높은 클릭률, 노출수, 비용을 기록하여 나이키가 운동화를 찾는 관련성 있는 청중에게 효과적으로 도달하고 있음을 보여줍니다. 나이키는 이 키워드에 대한 투자를 계속하고 추천 검색 광고 캠페인을 최적화하여 운동화 판매를 늘릴 수 있습니다.
# '''
#     if(prompt == '나이키 키워드에 대한 2024-03-17 ~ 2024-03-31 데이터를 가지고 가장 성과가 좋은 검색 광고 키워드는 무엇이었는지와 키워드의 성과를 분석해주세요.'): st.chat_message("assistant", avatar=GP_ICON).write(msg1)
#     if(prompt == '월별 평균 세션 지속 시간의 그래프를 그려주세요'):  st.image(get_image_base64(), caption="월별 평균 지속 시간")
        
    
# data = {
#     "unique_users": 366,
#     "unique_events": 19,
#     "unique_dates": 1,
#     "unique_timestamps": 2465,
#     "unique_previous_timestamps": 4,
#     "unique_event_values": 0,
#     "unique_bundle_ids": 3,
#     "unique_server_offsets": 2,
#     "unique_user_ids": 0,
#     "unique_first_touch_timestamps": 365
# }

# # # Convert data to DataFrame
# chart = alt.Chart(data_df).mark_line(point=True).encode(
#     x=alt.X('Category:N', title='Category'),
#     y=alt.Y('Values:Q', title='Values'),
#     tooltip=['Category', 'Values']
# ).properties(
#     title='Unique Data Metrics',
#     width=600
# )

# # Display the chart in Streamlit
# st.altair_chart(chart, use_container_width=True)