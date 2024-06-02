#폴더 경로는 /src 기준으로 작성한다.

# 프로젝트 정보. 
project_id = "lottecard-test"
region="asia-northeast3"

#서비스 계정 Key
service_acc_dev = "./key.json"
service_acc_prod = "/home/chatbot/key.json"

# 모델 정보.
# 모델은 여러개 등록해서 코드상에서 해당 목적에 맞게 구성
gemini_1_0_pro = "gemini-1.0-pro-002"
gemini_1_5_pro = "gemini-1.5-pro-preview-0514"
gemini_1_5_flash = "gemini-1.5-flash-preview-0514"

text_embedding_model = "text-multilingual-embedding-preview-0409"