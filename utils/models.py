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
import os
import re

import requests
from bs4 import BeautifulSoup, NavigableString

# utils가 있는
PATH_MODULE = os.path.abspath(__file__)
# 프로젝트 컨테이너 폴더 경로
ROOT_DIR = os.path.dirname(os.path.dirname(PATH_MODULE))
# data/ 폴더 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')

print(PATH_MODULE)
print(ROOT_DIR)
print(DATA_DIR)


class MelonCrawler:
    def search_song(self, q):
        """
        곡 명으로 멜론에서 검색한 결과 리스트를 리턴
        :param q: 검색할 곡 명
        :return: 결과 dict리스트
        """
        """
        1. http://www.melon.com/search/song/index.htm
            에 q={q}, section=song으로 parameter를 준 URL에
            requests를 사용해 요청
        2. response.text를 사용해 BeautifulSoup인스턴스 soup생성
        3. soup에서 적절히 결과를 가공
        4. 결과 1개당 Song인스턴스 한개씩
        5. 전부 리스트에 넣어 반환
        6. 완☆성
        """
        url = 'https://www.melon.com/search/song/index.htm'
        params = {
            'q': q,
            'section': 'song',
        }
        response = requests.get(url, params)
        soup = BeautifulSoup(response.text, 'lxml')
        tr_list = soup.select('form#frm_defaultList table > tbody > tr')
        # tr_list = soup.find('form', id='frm_defaultList').find('table').find('tbody').find_all('tr')

        result = []
        for tr in tr_list:
            # <a href="javascript:searchLog('web_song','SONG','SO','빨간맛','30512671');melon.play.playSong('26020103',30512671);" class="fc_gray" title="빨간 맛 (Red Flavor)">빨간 맛 (Red Flavor)</a>
            # song_id = re.search(r"searchLog\(.*'(\d+)'\)", tr.select_one('td:nth-of-type(3) a.fc_gray').get('href')).group(1)
            song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
            title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
            artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(
                strip=True)
            album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

            song = Song(song_id=song_id, title=title, artist=artist, album=album)
            result.append(song)
        return result


class Song:
    def __init__(self, song_id, title, artist, album):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album

        self._release_date = None
        self._lyrics = None
        self._genre = None
        self._producers = None

    def __str__(self):
        return f'{self.title} (아티스트: {self.artist}, 앨범: {self.album})'

    def get_detail(self, refresh_html=False):
        """
        자신의 _release_date, _lyrics, _genre, _producers를 채운다
        :return:
        """
        # 파일위치는 data/song_detail_{song_id}.html
        file_path = os.path.join(DATA_DIR, f'song_detail_{self.song_id}.html')
        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode) as f:
                # url과 parameter구분해서 requests사용
                url = f'https://www.melon.com/song/detail.htm'
                params = {
                    'songId': self.song_id,
                }
                response = requests.get(url, params)
                source = response.text
                # 만약 받은 파일의 길이가 지나치게 짧을 경우 예외를 일으키고
                # 예외 블럭에서 기록한 파일을 삭제하도록 함
                file_length = f.write(source)
                if file_length < 10:
                    raise ValueError('파일이 너무 짧습니다')
        except FileExistsError:
            print(f'"{file_path}" file is already exists!')
        except ValueError:
            # 파일이 너무 짧은 경우
            os.remove(file_path)
            return

        source = open(file_path, 'rt').read()
        soup = BeautifulSoup(source, 'lxml')
        # div.song_name의 자식 strong요소의 바로 다음 형제요소의 값을 양쪽 여백을 모두 잘라낸다
        # 아래의 HTML과 같은 구조
        # <div class="song_name">
        #   <strong>곡명</strong>
        #
        #              Heart Shaker
        # </div>
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

        # 리턴하지말고 데이터들을 자신의 속성으로 할당
        self.title = title
        self.artist = artist
        self.album = album
        self._release_date = release_date
        self._genre = genre
        self._lyrics = lyrics
        self._producers = {}

    @property
    def lyrics(self):
        # 만약 가지고 있는 가사정보가 없다면
        if not self._lyrics:
            # 받아와서 할당
            self.get_detail()
        # 그리고 가사정보 출력
        return self._lyrics


class Artist:

    def __init__(self, artist_id, name, url_img_cover, real_name):
        pass
        self.artist_id = artist_id
        self.name = name
        self.url_img_cover = url_img_cover
        self.real_name = None

        self._info = {}
        self._award_history = []
        self._introduction = {}
        self._activity_information = {}
        self._personal_information = {}
        self._related_information = {}

    def get_detail(self, artist_id, refresh_html=False):
        file_path = os.path.join(DATA_DIR, f'artist_detail_{artist_id}.html')
        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode) as f:
                # 아티스트 목록 가져오는 html
                url = 'https://www.melon.com/artist/detail.htm'
                params = {
                    'artistId': artist_id
                }
                response = requests.get(url, params)
                source = response.text
                f.write(source)
        except FileExistsError:
            print(f'"{file_path}" file is already exists!')

        source = open(file_path, 'rt').read()
        soup = BeautifulSoup(source, 'lxml')


        # award_history
        div_section_atistinfo01 = soup.find('div', class_="section_atistinfo01")
        if not div_section_atistinfo01 == None:
            dl = div_section_atistinfo01.find('dl', class_='list_define')
            award_history = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
            self._award_history = award_history


        # _introduction = {}
        div_section_atistinfo02 = soup.find('div', class_= "section_atistinfo02")
        if not div_section_atistinfo02 == None:
            div = div_section_atistinfo02.find('div', id='d_artist_intro')
            introduction_list = list()
            for i in div:
                if i.name == 'br':
                    introduction_list.append('\n')
                elif type(i) is NavigableString:
                    introduction_list.append(i.strip())

            introduction = ''.join(introduction_list)
            self._introduction = introduction

        # _activity_information = {}
        div_section_atistinfo03 = soup.find('div' , class_ = "section_atistinfo03")
        if not div_section_atistinfo03 == None:
            dl = div_section_atistinfo03.find('dl', class_='list_define')
            items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
            '''
            iterable은 멤버를 하나씩 반환 할 수 있는 object 를 의미한다. 
            '''
            # 나중에 info 에 여기있는 정보를 넣어주면 될꺼같다
            it = iter(items)
            activity_information = dict(zip(it, it))
            self._activity_information = activity_information

            div_section_atistinfo04 = soup.find('div', class_="section_atistinfo04")
            #_personal_information
        if not div_section_atistinfo04 == None:
            dl = div_section_atistinfo04.find('dl', class_='list_define')
            items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
            li = iter(items)
            personal_information = dict(zip(li,li))
            self._personal_information = personal_information

            div_section_atistinfo05 = soup.find('div', class_="section_atistinfo05")
            # _related_information
            if not div_section_atistinfo05 == None:
                button_sns = div_section_atistinfo05.find_all('button')
                address = [re.search(r".*\('(.*?)?'", item.get('onclick')).group(1) for item in button_sns]
                sns_name = [item.get_text() for item in button_sns]
                related_information_first = dict(zip(sns_name,address))
                dl = div_section_atistinfo05.find('dl', class_='list_define')
                items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
                it = iter(items)
                # 딕셔너리두개를 한개로 병합  Unpacking Generalizations
                related_information_second = dict(zip(it, it))
                related_information = {**related_information_first, **related_information_second}
                self._related_information = related_information

                # 기본 info 이미지, 이름, 본명
                wrap_dtl_atist = soup.find('div', class_='wrap_dtl_atist')
                url_img_cover = wrap_dtl_atist.find('span', id="artistImgArea").find('img').get('src')
                # 이미지가 없을 경우에는 url 주소가 없는 것처럼
                if url_img_cover == "http://cdnimg.melon.co.kr":
                    url_img_cover = ""
                name_div = wrap_dtl_atist.select_one('p.title_atist').text[5:]
                name = re.search(r'(\w+)\s', name_div).group(1)
                real_name = re.search(r'\((\w+)\)', name_div).group(1)
                self.url_img_cover = url_img_cover
                self.name = name
                self.real_name = real_name
                self.artist_id = artist_id
                # 그외 정보는 다른 딕셔너리와 리스트에서 추출
                debut = activity_information['데뷔']
                birthday = personal_information['생일']
                activity_type = activity_information['유형']
                agency = activity_information['소속사명']
                self._info = {
                    "데뷔": debut,
                    "생일": birthday,
                    "유형": activity_type,
                    "소속사": agency,
                    "수상이력": award_history[0]}




