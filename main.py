import util
import smart
import KEYWORDs


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


if __name__ == '__main__':
    get_book_data_from_smart_all(thumb_flag=False)
    # get_book_data_from_smart(thumb_flag=True)
