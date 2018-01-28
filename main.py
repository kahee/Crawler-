from utils.models import *

if __name__ == '__main__':
    crawler = MelonCrawler()

    artist = Artist("아이유","dsf","sdfs",None)
    artist.get_detail(261143)
    print(artist.info)
    print(artist.award_history)
    print(artist.activity_information)
    print(artist.personal_information)
    print(artist.related_information)
    print(artist.introduction)