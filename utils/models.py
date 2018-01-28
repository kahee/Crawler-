import re

import os
import requests
from bs4 import BeautifulSoup, NavigableString

# utils가 있는
PATH_MODULE = os.path.abspath(__file__)
# 프로젝트 컨테이너 폴더 경로
ROOT_DIR = os.path.dirname(os.path.dirname(PATH_MODULE))
# data/ 폴더 경로
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# 경로확인
print(PATH_MODULE)
print(ROOT_DIR)
print(DATA_DIR)

class MelonCrawler:
    def search_song(self,title):
        # search_song instance method
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

            song = Song(song_id=song_id,title=title,artist=artist,album=album)
            result.append(song)

        return result





class Song:

    # title,artist,album info get
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
        return f'{self.tilte} (아티스트 : {self.artist}, 앨범: {self.album})'

    @property
    def lyrics(self):
        if not self._lyrics:
            self.get_detail()
        else:
            return self._lyrics

    def get_detail(self, refresh_html = False):
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
                f.write(source)
        except FileExistsError:
            print(f'"{file_path}" file is already exists!')

        source = open(file_path, 'rt').read()
        soup = BeautifulSoup(source, 'lxml')

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

        self.title = title
        self.artist = artist
        self.album = album
        self._release_date = release_date
        self._genre = genre
        self._lyrics = lyrics
        self._producers = {}


class Artist:


    def __init__(self,artist_id,name,url_img_cover,real_name):
        self.artist_id = artist_id
        self.name = name
        self.url_img_cover = url_img_cover
        self.real_name = None

        self._info={}
        self._award_history =[]
        self._introduction = {}
        # self._activity_information = {}
        # self._personal_information = {}
        # self._related_information = {}
        pass
    """
    아티스트 상세 정보
    http://www.melon.com/artist/detail.htm?artistId=261143
    artist_detail_{artist_id}.html
    Artist의 인스턴스 메서드
    def get_detail(self)
        return 없이 자신의 속성 채우기
    """
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

            # 기본 정보 _info
            wrap_dtl_atist = soup.find('div', class_='wrap_dtl_atist')
            url_img_cover = wrap_dtl_atist.find('span', id="artistImgArea").find('img').get('src')
            name_div = wrap_dtl_atist.select_one('p.title_atist ').text[5:]
            name = re.search(r'(\w+)\s',name_div).group(1)
            real_name = re.search(r'\((\w+)\)', name_div).group(1)
            debut = wrap_dtl_atist.select_one('dl.atist_info > dd:nth-of-type(1)').get_text(strip=True)[:10]
            birthday = wrap_dtl_atist.select_one('dl.atist_info > dd:nth-of-type(2)').get_text(strip=True)
            artist_type = wrap_dtl_atist.select_one('dl.atist_info > dd:nth-of-type(3)').get_text(strip=True)
            agency = wrap_dtl_atist.select_one('dl.atist_info > dd:nth-of-type(4)').get_text(strip=True)
            award = wrap_dtl_atist.select_one('dl.atist_info > dd:nth-of-type(5)').get_text(strip=True)
            self.artist_id = artist_id
            self.name = name
            self.real_name = real_name
            result = list()
            result.append({'데뷔': debut,
                            '생일': birthday,
                            '활동유형':artist_type,
                            '소속사':agency,
                            '수상이력':award})
            self._info = result

            #_award_history
            list_define = soup.find('dl', class_="list_define").find_all("dd")
            for i in list_define:
                # 수상 (수상내역) 형식으로 변경
                award_detail = re.search(r'(.*?)\|(.*)', i.text)
                self._award_history.append(f'{award_detail.group(1)} ({award_detail.group(2)})')

             #_introduction
            div_artist_intro = soup.find('div', id ="d_artist_intro")

            introduction_list = list()
            for i in div_artist_intro:
                if i.name == 'br':
                    introduction_list.append('\n')
                elif type(i) is NavigableString:
                    introduction_list.append(i.strip())

            introduction = ''.join(introduction_list)
            self._introduction = introduction






    """
    아티스트 검색
http://www.melon.com/search/artist/index.htm?q=%EC%95%84%EC%9D%B4%EC%9C%A0&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form
검색 결과를
def search_artist(q):
    return class Artist의 목록
    """
    def search_artist(self, artist, refresh_html = False):
        # search_song instance method

        # artist-> self.artist 로 바꿔야함

        file_path = os.path.join(DATA_DIR, f'artist_{artist}.html')
        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode) as f:
                # 아티스트 목록 가져오는 html
                url = 'https://www.melon.com/search/artist/index.htm'
                params = {
                    'q': artist,
                    'section': 'searchGnbYn'
                }
                response = requests.get(url, params)
                source = response.text
                f.write(source)
        except FileExistsError:
            print(f'"{file_path}" file is already exists!')

        source = open(file_path, 'rt').read()
        soup = BeautifulSoup(source, 'lxml')

        atist_info = soup.find_all('div', class_='atist_info')
        result = []
        for i in atist_info:
            # 아티스트 고유번호
            artist_id_href = i.find('a', class_="ellipsis").get('href')
            artist_id = re.search(r"\('(\d+)'\);", artist_id_href).group(1)
            # 아티스트 이름
            artist = i.find('a', class_="ellipsis").text
            # 아티스트 정보
            info = i.find('dd', class_="gubun").get_text(strip=True)
            # 아티스트 장르
            genre = i.find('dd', class_="gnr").get_text(strip=True)[4:]
            result.append({
                'artist_id': artist_id,
                'artist' : artist,
                'info' : info,
                'genre': genre
            })

        return result