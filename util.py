import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import os
import pandas as pd
import URLs
import termcolor


def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
    }
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    return soup


def add_query(url, key_and_vals):
    """
    urlに，key_and_valsで指定したクエリ文字列を追加したurlを返却する．
    :param url:
    :param key_and_vals: ('keyword', 'value') の形式でクエリ文字列が格納されたリスト
    :return:
    """
    all_q = key_and_vals.copy()
    pr = urllib.parse.urlparse(url)
    included_q = urllib.parse.parse_qs(pr.query)
    for key in included_q:
        q_tuple = tuple([key, included_q[key][0]])
        all_q.append(q_tuple)
    l_qs = urllib.parse.urlencode(all_q)

    return urllib.parse.urlunparse(pr._replace(query=l_qs))


def download_file_from_url(url, filename, dir):
    if not os.path.isdir(dir):
        print('make {} dir.'.format(dir))
        os.mkdir(dir)

    save_path = os.path.join(dir, filename)

    if os.path.isfile(save_path):
        c_sentence = termcolor.colored('{} has been already existed.'.format(save_path), 'cyan')
        print(c_sentence)
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
    }
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request).read()

        # ファイルへの保存

        with open(save_path, mode="wb") as f:
            f.write(response)
            print('save {}.'.format(save_path))

    except (OSError, PermissionError, urllib.error.HTTPError) as e:
        error_sentence = termcolor.colored('caused {}, in {}'.format(e, save_path), 'red')
        print(error_sentence)


def is_str_in(str_list, text):
    for st in str_list:
        if st == text:
            return True

    return False


def append_book_info_to_csv(csv_path, info, dir):
    # タイトル -> title
    # タグ -> tags
    # サークル -> circles
    # キャラクター -> characters
    # 原作品 -> org_title
    # おすすめ度 -> recommendation
    # でコラム名をつける
    if not os.path.isdir(dir):
        print('make {} dir'.format(dir))
        os.mkdir(dir)
    csv_path = os.path.join(dir, csv_path)
    columns = ['title', 'tags', 'circles', 'characters', 'org_anime', 'recommendation', 'URL']
    tags_for_csv = ",".join(map(str, info['tags']))
    circles_for_csv = ",".join(map(str, info['circles']))
    characters_for_csv = ",".join(map(str, info['characters']))
    org_anime_for_csv = ",".join(map(str, info['org_anime']))
    append_col = [info['title'], tags_for_csv, circles_for_csv, characters_for_csv, org_anime_for_csv,
                  info['recommendation'], info['url']]
    df = pd.DataFrame([append_col], columns=columns)

    try:
        if os.path.isfile(csv_path):
            existed_csv = pd.read_csv(csv_path, encoding='utf_8_sig').iloc[:, 1:]

            if is_str_in(existed_csv['title'], info['title']):
                c_sentence = termcolor.colored('This book {} has been already got before.'.format(info['title']),
                                               'cyan')
                print(c_sentence)
                return False
            existed_csv = pd.concat([existed_csv, df])
            print('append {} data to {}.'.format(info['title'], csv_path))
            existed_csv.to_csv(csv_path, encoding='utf_8_sig')
            return True

        df.to_csv(csv_path, encoding='utf_8_sig')
        print('save {} data to {}.'.format(info['title'], csv_path))
        return True

    except PermissionError:
        e_sentence = termcolor.colored('{} is opened, so loading {} will be skipped.'.format(csv_path, info['title']),
                                       'red')
        print(e_sentence)


if __name__ == '__main__':
    q = []
    q.append(('type', '2'))
    q.append(('keyword', 'ジャンヌ・ダルク'))
    q.append(('from', 'list'))
    url = add_query(URLs.SMART_MAIN + URLs.SMART_LIST, q)
    get_soup(url)
    print(url)
