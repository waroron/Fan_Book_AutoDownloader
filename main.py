import util
import smart
import KEYWORDs
import pandas as pd
import os


def get_book_data_from_smart(anime_title, thumb_flag=True):
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
        get_book_data_from_smart(title, thumb_flag)


def get_all_elements(elem, tags_csv, csv_dir='info', csv_name='all_book_info.csv'):
    csv = util.get_csv(csv_dir, csv_name)
    tags = csv[elem]
    result = []

    save_path = os.path.join(csv_dir, tags_csv)
    for num, tag in enumerate(tags):
        tmp = util.split_words(tag)
        result.extend(tmp)
    result = list(set(result))

    result = pd.DataFrame(result)
    result.to_csv(save_path, encoding='utf_8_sig')
    print('saved to {}'.format(save_path))


if __name__ == '__main__':
    get_all_elements('tags', 'tags_list.csv')
    get_all_elements('characters', 'characters_list.csv')
    get_all_elements('circles', 'circles_list.csv')
    get_all_elements('org_anime', 'org_anime_list.csv')
    # get_book_data_from_smart_via_KEYWORDs(thumb_flag=False)
    # get_book_data_from_smart_all(thumb_flag=False)
    # get_book_data_from_smart(thumb_flag=True)
