import os
import re

import requests
from bs4 import BeautifulSoup


def get_top100_list(refresh_html=False):
    """
    실시간 차트 1~100위의 리스트 반환
    파일위치:
        data/chart_realtime.html
    :param refresh_html: True일 경우, 무조건 새 HTML파일을 사이트에서 받아와 덮어씀
    :return: 곡 정보 dict의 list
    """
    # utils가 있는
    path_module = os.path.abspath(__file__)
    print(f'path_module: \n{path_module}')

    # 프로젝트 컨테이너 폴더 경로
    root_dir = os.path.dirname(path_module)
    print(f'root_dir: \n{root_dir}')

    # data/ 폴더 경로
    path_data_dir = os.path.join(root_dir, 'data')
    print(f'path_data_dir: \n{path_data_dir}')

    # 만약에 path_data_dir에 해당하는 폴더가 없을 경우 생성해준다
    os.makedirs(path_data_dir, exist_ok=True)
    # 실시간 1~100위 웹페이지 주소
    url_chart_realtime = 'https://www.melon.com/chart/index.htm'
    # 실시간 1~100위 웹페이지 HTML을 data/chart_realtime.html 에 저장
    file_path = os.path.join(path_data_dir, 'chart_realtime.html')
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
        # song_info 가져옴
        info = tr.find('a',class_='song_info').get('href')
        # href 주소 잘라내기
        p = re.compile(r'.*\'(.*?)\'')
        # re.compile(r'\(\'(\d+)\'\)')
        # [.] = \. dot find
        song_info = re.search(p,info).group(1)


        rank = tr.find('span', class_='rank').text
        title = tr.find('div', class_='rank01').find('a').text
        artist = tr.find('div', class_='rank02').find('a').text
        album = tr.find('div', class_='rank03').find('a').text
        url_img_cover = tr.find('a', class_='image_typeAll').find('img').get('src')
        # http://cdnimg.melon.co.kr/cm/album/images/101/28/855/10128855_500.jpg/melon/resize/120/quality/80/optimize
        # .* -> 임의 문자의 최대 반복
        # \. -> '.' 문자
        # .*?/ -> '/'이 나오기 전까지의 최소 반복
        p = re.compile(r'(.*\..*?)/')
        url_img_cover = re.search(p, url_img_cover).group(1)

        result.append({
            'info': song_info,
            'rank': rank,
            'title': title,
            'url_img_cover': url_img_cover,
            'artist': artist,
            'album': album,
        })
    return result

def get_song_detail(song_id):
    """
    song_id에 해당하는 곡 정보 dict를 반환
    위의 get_top100_list의 각 곡 정보에도 song_id가 들어가도록 추가
    """
    # 굳 이안가져와서 도사용 할방법 이있 을꺼같다.

    # utils가 있는
    path_module = os.path.abspath(__name__)
    # 프로젝트 컨테이너 폴더 경로
    root_dir = os.path.dirname(path_module)
    # data/ 폴더 경로
    path_data_dir = os.path.join(root_dir, 'data')


    # song_info page
    url_song_info ='https://www.melon.com/song/detail.htm?songId='+str(song_id)

    # song_info.html 파일저장
    file_name = 'song:'+str(song_id)+'.html'
    file_path = os.path.join(path_data_dir, file_name)

    try:
        # refresh_html매개변수가 True일 경우, wt모드로 파일을 열어 새로 파일을 다운받도록 함
        file_mode = 'wt' if file_path else 'xt'
        with open(file_path, file_mode) as f:
            response = requests.get(url_song_info)
            source = response.text
            f.write(source)
    # xt모드에서 있는 파일을 열려고 한 경우 발생하는 예외
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')



    # 1. source변수에 위에 정의해놓은 file_path(  data/chart_realtime.html)의
    #       파일 내용을 읽어온 결과를 할당
    f = open(file_path, 'rt')
    source = f.read()
    f.close()
    # 2. soup변수에 BeautifulSoup클래스 호출에 source를 전달해 만들어진 인스턴스를 할당
    #    soup = BeautifulSoup(source)
    soup = BeautifulSoup(source, 'lxml')
    # 3. BeautifulSoup을 사용해 HTML을 탐색하며 dict의 리스트를(result) 생성, 마지막에 리턴


    entry = soup.find('div', class_='entry')
    title = entry.find('div', class_='song_name').text
    p = re.compile(r'\s+')
    song_name = re.sub(p, '', title)
    artist = entry.find('div', class_='artist').find('a').text
    info_list = soup.find('dl', class_='list')
    album = info_list.find_all("dd")[0].text
    rel_date = info_list.find_all("dd")[1].text
    genre = info_list.find_all("dd")[2].text
    format = info_list.find_all("dd")[3].text


    lyric = soup.find('div', class_='lyric')
    print(lyric)
    # p = re.compile(r'.(\s+)(.*)$',re.DOTALL
    # result = re.search(p, lyric)
    # print(result)
    print(song_name[2:],artist, album, rel_date, genre, format)
    #
    # result.append({
    #     'title': song_name[2:],
    #       'artist': artist,
    #     'album': album,
    #     'rel_date': rel_date,
    #     'genre': genre,
    #     'format': format,
    #       'lyric' : lyric
    # })

def io_html(html_url, refresh_html=None):

    # utils가 있는
    path_module = os.path.abspath(__file__)
    print(f'path_module: \n{path_module}')
    # 프로젝트 컨테이너 폴더 경로
    root_dir = os.path.dirname(path_module)
    print(f'root_dir: \n{root_dir}')
    # data/ 폴더 경로
    path_data_dir = os.path.join(root_dir, 'data')
    print(f'path_data_dir: \n{path_data_dir}')

    # 만약에 path_data_dir에 해당하는 폴더가 없을 경우 생성해준다
    os.makedirs(path_data_dir, exist_ok=True)

    # 웹페이지 HTML을 data/chart_realtime.html 에 저장
    file_path = os.path.join(path_data_dir, html_url)

    try:

        # refresh_html매개변수가 True일 경우, wt모드로 파일을 열어 새로 파일을 다운받도록 함
        file_mode = 'wt' if refresh_html else 'xt'
        with open(file_path, file_mode) as f:
            response = requests.get(html_url)
            source = response.text
            f.write(source)

    # xt모드에서 있는 파일을 열려고 한 경우 발생하는 예외
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')

