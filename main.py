import util
import smart
import KEYWORDs
import re
import pandas as pd
import os


def get_book_data_from_smart(anime_title, thumb_flag=True, ):
    csv_name = 'all_book_info.csv'
    dir_name = 'info'
    if thumb_flag is False:
        thumb_dir = None
    else:
        thumb_dir = 'thumb2'

    q = []
    q.append(('type', '1'))
    q.append(('keyword', anime_title))
    smart.get_book_data_from_secified_query(query=q, csv_name=csv_name, dir_name=dir_name, thumb_dir=thumb_dir)


def get_book_data_from_smart_via_KEYWORDs(thumb_flag=True):
    for keyword in KEYWORDs.ORG_TITLES:
        get_book_data_from_smart(keyword, thumb_flag)


def get_book_data_from_smart_all(thumb_flag=True):
    titles = smart.get_all_anime_titles()
    print(titles)

    for title in titles:
        print(title)
        get_book_data_from_smart(title,thumb_flag)


def get_all_tags(tags_csv, csv_dir='info', csv_name='all_book_info.csv'):
    csv = util.get_csv(csv_dir, csv_name)
    tags = csv['tags']
    add = []        # 共通集合
    subtract = []   # 共通集合の補集合
    result = []

    save_path = os.path.join(csv_dir, tags_csv)

    for num in range(len(tags)):
        tmp = util.split_words(tags[num])

        tmp = [s for s in tmp if not re.match('....-..-..', s)]

        add = list(set(result) & set(tmp))
        subtract = list(set(result) ^ set(tmp))
        result = add.copy()
        result.extend(subtract)

    result = pd.DataFrame(result)
    result.to_csv(save_path, encoding='utf_8_sig')
    print('saved to {}'.format(save_path))


if __name__ == '__main__':
    # get_all_tags('all_tags.csv')
    get_book_data_from_smart_via_KEYWORDs(thumb_flag=False)
    # get_book_data_from_smart_all(thumb_flag=False)
    # get_book_data_from_smart(thumb_flag=True)
