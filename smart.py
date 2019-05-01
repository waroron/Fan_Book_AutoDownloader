from bs4 import BeautifulSoup
import urllib.request
import URLs
import util
import termcolor


THUMB_NAME_N = 16


def get_all_new_urls():
    """
    同人すまーとの，新着作品ページで紹介されているすべての作品のページのURLを取得し，その文字列を返却する．
    :param soup: 新着作品ページのsoup
    :return: すべての新着作品のページURLのリスト
    """
    soup = util.get_soup(URLs.SMART_MAIN + URLs.SMART_NEW)
    all_urls_soup = soup.find('ul', class_='package-list row tab-content_description')
    all_urls_soup = all_urls_soup.find_all('a', attrs={"target": "_blank"})
    urls = []

    for urls_soup in all_urls_soup:
        book_url = urls_soup.get('href')
        urls.append(URLs.SMART_MAIN + book_url)

    return urls


def get_specified_book_urls(type, keyword):
    search_url = URLs.SMART_MAIN + URLs.SMART_LIST
    query = [('from', 'list'), (str(type), keyword)]
    shaped_url = util.add_query(search_url, query)

    # 同人すまーとは，
    # type = 1: 原作タイトル 2: キャラクター名
    # keyword: typeで指定したものに対する検索ワード

    return shaped_url


def get_urls_from_searching_page(searched_url):
    urls = []
    soup = util.get_soup(searched_url)
    tmp = soup.find('div', class_='list-all')
    book_list_soup = tmp.find('ul', class_='package-list row tab-content_description')
    each_book_soups = book_list_soup.find_all('li', class_='col s4 m3 l2')

    for book_soup in each_book_soups:
        a_soup = book_soup.find('a', attrs={"target": "_blank"})
        href = a_soup.get('href')
        urls.append(URLs.SMART_MAIN + href)

    return urls


def get_urls_from_all_searching_page(searched_url):
    all_urls = []
    page = 1
    while True:
        page_query = [('page', str(page))]
        this_url = util.add_query(searched_url, page_query)
        urls = get_urls_from_searching_page(this_url)

        if len(urls) < 1:
            break
        else:
            all_urls.extend(urls)
        page += 1

    return all_urls


def get_attrs_from_soup(soup):
    """
    同人すまーと内の作品ページの，作品情報を取得するため，
    1つ前の作品情報のsoupを渡し，その次のsoup内のaタグで示された情報をリストにして
    返却する，
    その際のsoupも，次の情報を取得するために返却する．
    :param soup:
    :return:
    """
    attrs = []
    next_soup = soup.find_next()
    a_soups = next_soup.find_all('a')
    for a in a_soups:
        attrs.append(a.text.strip())
    return attrs, a_soups


def _get_book_data_from_its_page(keyword, soup):
    detail_box_soup = soup.find('span', class_=keyword)
    if detail_box_soup is None:
        return [""]
    target_soup = detail_box_soup.find_next()

    attrs = []
    a_soups = target_soup.find_all('a')
    for a in a_soups:
        attrs.append(a.text.strip())

    return attrs


def get_book_info_from_url(url):
    """
    作品ページのURLから，作品タイトル，作品公開日，原作名などの作品情報と，作品のpdfが公開されているURLを取得し，
    辞書にして返却する．
    :param url: 作品URL
    :return: 作品に関連する情報を含んだ辞書
    """
    info = {}
    soup = util.get_soup(url)
    tmp_soup = soup.find(string='ダウンロード')

    try:
        book_title = soup.find('h1', class_='list-pickup-header margin-bottom-0 card-panel white-text blue accent-2').text
        first_soups = soup.find_all('span', class_='anime-icon')
        attr_first_soup = first_soups[0]

        # ページのレイアウト構成では，原作タイトル，キャラクター，サークル，タグ，更新日，発行日，おすすめ順の順
        # (2019/05/01追記)
        # 実際にクラウドにpdfデータを置いとくのは容量的によろしくないので，pdfへのURL
        # また，サムネイル画像はサイズは大きくはないが，同人誌リストを表示するたびに，
        # 複数の本のサムネイル画像へのrequestを要求するため，request回数制限の上限への到達，及びそれに伴う料金発生が
        # 考えられる．それらを防ぐために，サムネイル画像へのURLも保存する
        # 「原作」のところから下に順番に，キャラクター名，サークル名，タグとなっていることが前提
        # -->
        org_titles = _get_book_data_from_its_page('anime-icon', soup)
        characters = _get_book_data_from_its_page('character-icon', soup)
        circles = _get_book_data_from_its_page('circle-icon', soup)
        tags = _get_book_data_from_its_page('tag-icon', soup)

        info['title'] = book_title
        info['org_anime'] = org_titles
        info['characters'] = characters
        info['circles'] = circles
        info['tags'] = tags

        # サムネイル画像のURLと，おすすめ度を取得
        view_soup = soup.find('div', class_='bookview-wrap')
        show_soup = view_soup.find('div', class_='show-relative')
        img_soup = show_soup.find('img')
        info['thumb_url'] = img_soup.get('src')
        info['thumb_name'] = util.random_name(THUMB_NAME_N) + '.jpeg'
        star_soup = view_soup.find_all('i', class_='material-icons star')
        info['recommendation'] = len(star_soup)

        next_url_soup = tmp_soup.find_parent().find_parent()
        next_url = next_url_soup.get('href')

        soup = util.get_soup(URLs.SMART_MAIN + next_url)
        button_soup = soup.find(string='PDFダウンロード')
        pdf_url_soup = button_soup.find_parent().find_parent()
        pdf_url = pdf_url_soup.get('href')
        info['url'] = pdf_url

        return info
    except AttributeError as e:
        e_sentence = termcolor.colored('caused {}'.format(e), 'red')
        print(e_sentence)


def download_pdf_from_urls(url, dir):
    """
    作品の公開されているURLから，pdfファイルをダウンロードし，dirに保存する．
    :param url: 作品URL
    :param dir: 保存先
    :return:
    """
    book_info = get_book_info_from_url(url)
    util.download_file_from_url(book_info['url'], book_info['title'] + '.pdf', dir)

    return book_info


def download_all_new_books(csv_path, dir):
    """
    同人すまーとの新着作品をすべてダウンロードし，dirに保存する．
    :param dir:
    :return:
    """
    # soup = util.get_soup(URLs.SMART_MAIN + URLs.SMART_NEW)
    all_new_urls = get_all_new_urls()

    for url in all_new_urls:
        book_info = download_pdf_from_urls(url, dir)
        util.append_book_info_to_csv(csv_path, book_info)


def get_book_data_from_secified_query(query, csv_name, dir_name='info', thumb_dir='thumb'):
    searched_url = util.add_query(URLs.SMART_MAIN + URLs.SMART_LIST, query)
    urls = get_urls_from_all_searching_page(searched_url)
    for url in urls:
        try:
            info = get_book_info_from_url(url)
            util.append_book_info_to_csv(csv_path=csv_name, dir=dir_name, info=info)
            if thumb_dir is not None:
                thumb_name = info['thumb_name']
                util.download_file_from_url(info['thumb_url'], thumb_name, thumb_dir)
        except:
            import traceback
            traceback.print_exc()
            continue


def get_all_anime_titles():
    titles =[]
    q = []
    q.append(('from', 'sidebar_icon'))
    searched_url = util.add_query(URLs.SMART_MAIN + URLs.SMART_PRODUCT, q)
    soup = util.get_soup(searched_url)

    row = soup.find('ul', class_='row')
    lists = row.find_all('li', class_='category-list card-panel col s12 m12 l6')

    for list_ in lists:
        title = list_.find('span', class_='title').get_text()
        titles.append(title)

    return titles


def _test():
    # download_all_new_books('test')
    info = get_book_info_from_url('http://d-smart.jp/doujinshi3/show-m.php?g=20190419&dir=001&page=0&from=list&from=package-list')
    # info = download_pdf_from_urls('http://d-smart.jp/doujinshi3/show-m.php?g=20190419&dir=001&page=0&from=list&from=package-list', 'pdfs')
    util.append_book_info_to_csv('test.csv', info)
    # soup = util.get_soup(URLs.SMART_MAIN + URLs.SMART_NEW)
    # get_all_new_urls(soup)


def test_search_and_get_urls():
    q = []
    q.append(('type', '2'))
    q.append(('keyword', 'ジャンヌ・ダルク'))
    # q.append(('from', 'list'))
    searched_url = util.add_query(URLs.SMART_MAIN + URLs.SMART_LIST, q)
    print('searching url is {}'.format(searched_url))

    urls = get_urls_from_all_searching_page(searched_url)
    print('searching {}s results  are follows'.format(len(urls)))
    for url in urls:
        get_book_info_from_url(url)
        print(url)


def test_save_info_from_searched_result():
    csv_name = 'all_book_info.csv'
    dir_name = 'info'
    thumb_dir = 'thumb'
    q = []
    q.append(('type', '2'))
    q.append(('keyword', 'ジャンヌ・ダルク'))
    searched_url = util.add_query(URLs.SMART_MAIN + URLs.SMART_LIST, q)
    print('searching url is {}'.format(searched_url))

    urls = get_urls_from_all_searching_page(searched_url)
    for url in urls:
        info = get_book_info_from_url(url)
        util.append_book_info_to_csv(csv_path=csv_name, dir=dir_name, info=info)
        # thumb_name = info['title'] + '_thumb.jpg'
        thumb_name = info['thumb_name']
        util.download_file_from_url(info['thumb_url'], thumb_name, thumb_dir)


if __name__ == '__main__':
    test_search_and_get_urls()
    # test_save_info_from_searched_result()
