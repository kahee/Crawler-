import os
import re

import requests
from bs4 import BeautifulSoup, NavigableString

"""
아티스트 검색
http://www.melon.com/search/artist/index.htm?q=%EC%95%84%EC%9D%B4%EC%9C%A0&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form
검색 결과를
def search_artist(q):
    return class Artist의 목록
아티스트 상세 정보
http://www.melon.com/artist/detail.htm?artistId=261143
artist_detail_{artist_id}.html
Artist의 인스턴스 메서드
    def get_detail(self)
        return 없이 자신의 속성 채우기
아티스트의 곡
http://www.melon.com/artist/song.htm?artistId=261143
Artist의 인스턴스 메서드
    def get_songs(self)
        return Song의 list
"""


# utils가 있는
PATH_MODULE = os.path.abspath(__file__)

# 프로젝트 컨테이너 폴더 경로
ROOT_DIR = os.path.dirname(PATH_MODULE)

# data/ 폴더 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')


def get_top100_list(refresh_html=False):
    """
    실시간 차트 
    실시간 차트 1~100위의 리스트 반환
    파일위치:
        data/chart_realtime.html
    :param refresh_html: True일 경우, 무조건 새 HTML파일을 사이트에서 받아와 덮어씀
    :return: 곡 정보 dict의 list
    """
    # 만약에 path_data_dir에 해당하는 폴더가 없을 경우 생성해준다
    os.makedirs(DATA_DIR, exist_ok=True)

    # 실시간 1~100위 웹페이지 주소
    url_chart_realtime = 'https://www.melon.com/chart/index.htm'

    # 실시간 1~100위 웹페이지 HTML을 data/chart_realtime.html 에 저장
    file_path = os.path.join(DATA_DIR, 'chart_realtime.html')
    try:
        # refresh_html매개변수가 True일 경우, wt모드로 파일을 열어 새로 파일을 다운받도록 함
        file_mode = 'wt' if refresh_html else 'xt'
        with open(file_path, file_mode) as f:
            response = requests.get(url_chart_realtime)
            source = response.text
            f.write(source)
    # xt모드에서 있는 파일을 열려고 한 경우 발생하는 예외
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')

    # 1. source변수에 위에 정의해놓은 file_path(data/chart_realtime.html)의
    #       파일 내용을 읽어온 결과를 할당
    f = open(file_path, 'rt')
    source = f.read()
    f.close()
    # 2. soup변수에 BeautifulSoup클래스 호출에 source를 전달해 만들어진 인스턴스를 할당
    #    soup = BeautifulSoup(source)
    soup = BeautifulSoup(source, 'lxml')
    # 3. BeautifulSoup을 사용해 HTML을 탐색하며 dict의 리스트를(result) 생성, 마지막에 리턴

    result = []
    for tr in soup.find_all('tr', class_=['lst50', 'lst100']):
        rank = tr.find('span', class_='rank').text
        title = tr.find('div', class_='rank01').find('a').text
        artist = tr.find('div', class_='rank02').find('a').text
        album = tr.find('div', class_='rank03').find('a').text
        url_img_cover = tr.find('a', class_='image_typeAll').find('img').get('src')
        song_id_href = tr.find('a', class_='song_info').get('href')
        song_id = re.search(r"\('(\d+)'\)", song_id_href).group(1)
        # http://cdnimg.melon.co.kr/cm/album/images/101/28/855/10128855_500.jpg/melon/resize/120/quality/80/optimize
        # .* -> 임의 문자의 최대 반복
        # \. -> '.' 문자
        # .*?/ -> '/'이 나오기 전까지의 최소 반복
        p = re.compile(r'(.*\..*?)/')
        url_img_cover = re.search(p, url_img_cover).group(1)

        result.append({
            'rank': rank,
            'title': title,
            'url_img_cover': url_img_cover,
            'artist': artist,
            'album': album,
            'song_id': song_id,
        })
    return result



def search_song(title):
    """
    곡 명으로 멜론에서 검색한 결과 리스트를 리턴
    :param title: 검색할 곡 명
    :return: 결과 dict리스트
    """
    """
    1. http://www.melon.com/search/song/index.htm
        에 q={title}, section=song으로 parameter를 준 URL에
        requests를 사용해 요청
    2. response.text를 사용해 BeautifulSoup인스턴스 soup생성
    3. soup에서 적절히 결과를 가공
    4. 결과 1개당 dict한개씩 구성
    5. 전부 리스트에 넣어 반환
    6. 완☆성
    """
    url = 'https://www.melon.com/search/song/index.htm'
    params = {
        'q': title,
        'section': 'song',
    }
    response = requests.get(url, params)
    soup = BeautifulSoup(response.text, 'lxml')
    tr_list = soup.select('form#frm_defaultList table > tbody > tr')

    result = []
    for tr in tr_list:
        song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get("value")
        title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
        artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(
            strip=True)
        album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

        result.append({
            'title': title,
            'artist': artist,
            'album': album,
        })
    return result
