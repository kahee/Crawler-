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
        self.album  = album
        self._release_date = release_date
        self._genre = genre
        self._lyrics = lyrics
        self._producers = {}
