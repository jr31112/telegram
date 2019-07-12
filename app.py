import pprint
import random 

import requests
from decouple import config
from flask import Flask, request

app = Flask(__name__)
token = config('TELEGRAM_TOKEN')
base_url = f'https://api.telegram.org/bot{token}'

naver_client_id = config('NAVER_CLIENT_ID')
naver_client_secret = config('NAVER_CLIENT_SECRET')

headers = {
    'X-Naver-Client-Id': naver_client_id,
    'X-Naver-Client-Secret': naver_client_secret
}

@app.route(f'/{token}', methods=['POST'])
def telegram():
    response = request.get_json()
    # 사진 파일이 온다면,
    if response.get('message').get('photo'):
        chat_id = response.get('message').get('chat').get('id')
        # 사진 파일의 id를 가져온다.
        file_id = response.get('message').get('photo')[-1].get('file_id')
        # 텔레그램 서버에 파일의 경로를 받아온다.
        file_response = requests.get(f'{base_url}/getFile?file_id={file_id}').json()
        # 파일 경로를 통해 URL 만든다.
        file_path = file_response.get('result').get('file_path')
        file_url = f'https://api.telegram.org/file/bot{token}/{file_path}' # 파일 URL
        print(file_url)
        response = requests.get(file_url, stream=True)
        image = response.raw.read()
        # 2. URL 설정
        naver_url = 'https://openapi.naver.com/v1/vision/celebrity'
        response = requests.post(naver_url, 
                                headers=headers,
                                files={'image': image}).json()
        
        if response.get('faces'):
            best = response.get('faces')[0].get('celebrity')
            if best.get('confidence') > 0.2:
                text = f"{best.get('confidence')*100}%만큼 {best.get('value')}를 닮으셨네요~"
            else:
                text = "연예인을 닮지 않았네요...."
        else:
            text = '사람 아닌듯;;'
        api_url = f'{base_url}/sendMessage?chat_id={chat_id}&text={text}'
        requests.get(api_url) # 메시지 전송
    # text가 온다면,
    elif response.get('message').get('text'):
        # 사용자가 보낸 메시지를 text 변수에 저장, 사용자 정보는 chat_id에 저장
        text = response.get('message').get('text')
        chat_id = response.get('message').get('chat').get('id')
        if '/번역 ' == text[0:4]:
            data = {
                'source': 'ko',
                'target': 'en',
                'text': text[4:]
            }
            if '중국어' in text:
                data['target'] = 'zh-CN'
                
            naver_url = 'https://openapi.naver.com/v1/papago/n2mt'
            response = requests.post(naver_url, headers=headers, data=data).json()
            text = response.get('message').get('result').get('translatedText')
        # if 인사말이 오면, 나만의 인사해주기
        elif '안녕' in text or 'hi' in text:
            text = '안녕, 나는 봇?' 
        elif '로또' in text:
            text = sorted(random.sample(range(1, 46), 6))



        # 마지막! url 만들어서 메시지 보내기
        api_url = f'{base_url}/sendMessage?chat_id={chat_id}&text={text}'
        requests.get(api_url) # 메시지 전송
    return 'Ok', 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
