import util
import smart
import KEYWORDs


def get_book_data_from_smart(thumb_flag=True):
    csv_name = 'all_book_info2.csv'
    dir_name = 'info2'
    thumb_dir = 'thumb2'

    for keyword in KEYWORDs.ORG_TITLES:
        q = []
        q.append(('type', '1'))
        q.append(('keyword', keyword))
        smart.get_book_data_from_secified_query(query=q, csv_name=csv_name, dir_name=dir_name, thumb_dir=thumb_dir)


if __name__ == '__main__':
    get_book_data_from_smart(thumb_flag=True)
