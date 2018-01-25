from utils import get_top100_list

if __name__ == '__main__':
    result = get_top100_list()
    for item in result:
        print(f'{item["rank"]:3}: {item["title"]}')