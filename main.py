
from utils.models import *

if __name__ == '__main__':
    crawler = MelonCrawler()

    artist = Artist('dfdf','dfsadf','dsaf','dsf')
    artist.get_detail(261143)

    print(artist._info)
    # print(artist._introduction)
    pratice = Artist('dfdf','dfsadf','dsaf','dsf')
    pratice.get_detail(167076)

    print(pratice._info)
    # print(pratice._introduction)
    # print(artist.info)
    # print(artist.award_history)
    # print(artist.activity_information)
    # print(artist.personal_information)
    # print(artist.related_information)
    # print(artist.introduction)
