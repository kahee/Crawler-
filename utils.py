import os
import requests

def get_top100_list(refresh_html=False):

    """
    실시간 차트 1~100위의 리스트 반환
    파일위치:
    현재 파일(모듈)의 위치를 사용한 상위 디렉토리 경로

    (crawler디렉토리):
    os.path.dirname(os.path.abspath(__name__))
    :return:
   """
    # 프로젝트 컨테이너 폴더 경로
    path_module= os.path.abspath(__name__)
    print(f'path_module:{path_module}')
    root_dir  = os.path.dirname(path_module)
    print(f'path_dir :{root_dir}')
    path_data_dir = os.path.join(root_dir,'data')
    print(f'path_data_dir:{path_data_dir}')
    os.makedirs(path_data_dir,exist_ok=True)

    # data/ 폴더 경로
    url_chart_realtime='http://www.melon.com/chart/index.htm'

    file_path = os.path.join(path_data_dir, 'chart_realtime.html')
    try:
            file_mode  = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode) as f:
                response = requests.get(url_chart_realtime)
                source = response.text
                f.write(source)


    except FileExistsError as e:
        print(f'"{file_path}" file is already exisits!')



# melon_chart50 = list()
# for tr in soup.find_all('tr', class_='lst50'):
#     rank = tr.find('span', class_="rank").text
#     title = tr.find('div', class_='rank01').find('a').text
#     artist = tr.find('div', class_='rank02').find('a').text
#     album = tr.find('div', class_='rank03').find('a').text
#     url_img_cover = tr.find('a', class_='image_typeAll').find('img').get('src')
#     p = re.compile(r'(.*\..*?)/')
#     url_img_cover = re.search(p, url_img_cover).group()
#
#     melon_chart50.append({
#         'rank': rank, 'title': title,
#         'url_img_cover': url_img_cover,
#         'artist': artist, 'album': album})
