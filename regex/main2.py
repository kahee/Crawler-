from regex.utila import *

# f = open('melon.html','rt')
# source = f.read()
# f.close()
# close를 안해주도 된다. 파일을 열어준 객체가 사라지기 때문이다.
# 로컬 html 불러오기
source = open('melon.html','rt').read()

# 위의 소스에서 <div class="ellipsis rank01> ~ </div>부분의 텍스트
# div_rank01 변수에 할당
PATTERN_DIV_RANK01 = re.compile(r'<div class="ellipsis rank01">.*?</div>', re.DOTALL)
# div_rank02
PATTERN_DIV_RANK02 = re.compile(r'<div class="ellipsis rank02">.*?</div>', re.DOTALL)
# div_rank03
PATTERN_DIV_RANK03 = re.compile(r'<div class="ellipsis rank03">.*?</div>', re.DOTALL)

# div_rank01 변수에 있는 문자열에서
# <a href=....>(내용)</a>
# title/ artist/album
PATTERN_A_CONTENT = re.compile(r'<a.*?>(.*?)</a>')

# 앨범
found_album = PATTERN_DIV_RANK03.finditer(source)
album_list = list()
for i in found_album:
    result = PATTERN_A_CONTENT.search(i.group())
    album_list.append(result.group(1))

# 가수
found_list = PATTERN_DIV_RANK02.finditer(source)
artist_list = list()
for i in found_list:
    result = PATTERN_A_CONTENT.search(i.group())
    artist_list.append(result.group(1))

# 타이틀
match_list = re.finditer(PATTERN_DIV_RANK01,source)
title_list = list()
for match_div_rank01 in match_list:
    div_rank01_content = match_div_rank01.group()
    result = re.search(PATTERN_A_CONTENT,div_rank01_content).group(1)
    title_list.append(result)


# 딕셔너리 만드는 법
result_list = list(zip(title_list,artist_list,album_list))
final_list = list()

for index,i in enumerate(result_list):
    result_dict = dict()
    result_dict["rank"] = index+1
    result_dict["title"] = i[0]
    result_dict["artist"] = i[1]
    result_dict["ablum"] = i[2]
    final_list.append(result_dict)

for i in final_list :
    print(i)