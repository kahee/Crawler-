import os
import re

import requests
from bs4 import BeautifulSoup, NavigableString

# utils가 있는
PATH_MODULE = os.path.abspath(__file__)

# 프로젝트 컨테이너 폴더 경로
ROOT_DIR = os.path.dirname(PATH_MODULE)

# data/ 폴더 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')


def get_top100_list(refresh_html=False):
    """
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


def get_song_detail(song_id, refresh_html=False):
    """
    song_id에 해당하는 곡 정보 dict를 반환
    위의 get_top100_list의 각 곡 정보에도 song_id가 들어가도록 추가
    http://www.melon.com/song/detail.htm?songId=30755375
    위 링크를 참조
    파일명
        song_detail_{song_id}.html
    :param song_id: Melon사이트에서 사용하는 곡의 고유 ID값
    :param refresh_html: 이미 다운받은 HTML데이터가 있을 때 기존 데이터를 덮어씌울지 여부
    :return: 곡 정보 dict
    """
    # 파일위치는 data/song_detail_{song_id}.html
    file_path = os.path.join(DATA_DIR, f'song_detail_{song_id}.html')
    try:
        file_mode = 'wt' if refresh_html else 'xt'
        with open(file_path, file_mode) as f:
            # url과 parameter구분해서 requests사용
            url = f'https://www.melon.com/song/detail.htm'
            params = {
                'songId': song_id,
            }
            response = requests.get(url, params)
            source = response.text
            f.write(source)
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')

    source = open(file_path,'rt').read()
    soup = BeautifulSoup(source,'lxml')

    div_entry = soup.find('div', class_='entry')
    title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()
    artist = div_entry.find('div', class_='artist').get_text(strip=True)
    # 앨범, 발매일, 장르...에 대한 Description list
    dl = div_entry.find('div', class_='meta').find('dl')
    # isinstance(인스턴스, 클래스(타입))
    # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
    items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
    it = iter(items)
    description_dict = dict(zip(it, it))

    album = description_dict.get('앨범')
    release_date = description_dict.get('발매일')
    genre = description_dict.get('장르')

    div_lyrics = soup.find('div', id='d_video_summary')

    lyrics_list = []
    for item in div_lyrics:
        if item.name == 'br':
            lyrics_list.append('\n')
        elif type(item) is NavigableString:
            lyrics_list.append(item.strip())
    lyrics = ''.join(lyrics_list)

    return {
        'title': title,
        'artist': artist,
        'album': album,
        'release_date': release_date,
        'genre': genre,
        'lyrics': lyrics,
        # 작사/작곡은 주말 숙제 포함
        'producers': {
            '작사': ['별들의 전쟁'],
            '작곡': ['David Amber', 'Sean Alexander'],
            '편곡': ['Avenue52'],
        },
    }