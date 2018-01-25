# 1. requests를 사용해서 주소에 get()요청
# 2. 1번 결과를 response 변수에 할당
# 3. response 변수의 .text 속성값을 source 변수에 할당 (응답에서 텍스트 데이터를 가져옴)
# 4. source 변수에 있는 내용은 문자열 데이터임
# 5. f = open(경로, 'wt')를 이용해 쓰기 가능한 파일 변수 'f'를 선언
# 6. 선언한 파일 변수 f 에 source  변수에 있는 내용을 기록
# 7. 파일 변수를 닫아줌
# 8. melon.html 에 해당 내용이 잘 저장되어있는지 확인
# 9. 이 모든 내용을 save()함수에 넣고, save_melon 모듈의 __name__이 "__main__" 일때만 실행하도록 함

import requests

def save():
    response = requests.get('https://www.melon.com/chart/index.htm')
    source = response.text
    # with open('melon.html','wt') as f :
    #     f.write(source)

    f = open('melon.html', 'wt')
    f.write(source)
    f.close()

    if __name__ == '__main__':
        save()