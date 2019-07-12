import pprint

import requests
from decouple import config # 파이썬에서 환경변수 관리하는 패키지

# 1. 토큰 및 기본 url 설정
token = config('TELEGRAM_TOKEN') # .env 설정값 가져오기
base_url = f'https://api.telegram.org/bot{token}/'

# 2. getUpdates 정보 가져오기
response = requests.get(base_url+'getUpdates').json()
# print(response)

# 3. 나의 chat_id 가져오기
chat_id = response.get('result')[0].get('message').get('chat').get('id')
# 670131877

# 4. chat_id에 메세지 보내기
# 4-1 요청보낼 URL 만들기
# sendMessage?chat_id=670131877&text=%EC%95%88%EB%85%95
text='안녕'
api_url = f'{base_url}sendMessage?chat_id={chat_id}&text={text}'
requests.get(api_url)