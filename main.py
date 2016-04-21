#-*- coding: UTF-8 -*-
import urllib
import re
import urlparse
import chardet

import variables
from const import const

invalid_ends = ["js", "css", "xml", "ico", "svg"]
invalid_contains = ["javascript", "<", ">", "{", "}"]
invalid_equals = {"/", "#", "href"}
invalid_starts = ["\""]

results = []

global count
count = 0


def get_html(url):
    global HOST
    try:
        page = urllib.urlopen(url)
        html = page.read()
        if const.need_check_charset:
            charset = check_charset(html)
            html = html.decode(charset).encode("UTF-8")
        result = urlparse.urlparse(url)
        HOST = result.scheme + "://" + result.netloc
        return html
    except:
        return ""


def check_charset(data):
    if const.simple_check_charset:
        types = ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']  # 可以添加其他字符编码
        for charset1 in types:
            try:
                data.decode(charset1)
            except Exception, ex:
                # print Exception,":",ex
                continue
            if not charset1:
                return 'utf-8'
            else:
                return charset1
    else:
        charset2 = chardet.detect(data)
        return charset2['encoding']


def url_join(base, url):
    url1 = urlparse.urljoin(base, url)
    arr1 = urlparse.urlparse(url1)
    return urlparse.urlunparse((arr1.scheme, arr1.netloc, arr1[2], arr1.params, arr1.query, arr1.fragment))


def is_valid_url(url):
    for invalid_end in invalid_ends:
        if url.endswith(invalid_end):
            return False
    for invalid_contain in invalid_contains:
        if url.find(invalid_contain) >= 0:
            return False
    for invalid_equal in invalid_equals:
        if url == invalid_equal:
            return False
    for invalid_start in invalid_starts:
        if url.startswith(invalid_start):
            return False
    return True


def do_write_file():
    f = open('./result.txt', 'w')
    for url in results:
        if const.isRelease:
            f.write(url)
            f.write("\n")
    f.close()
    print len(results)


def check_host(host, url):
    arr2 = urlparse.urlparse(url)
    if not variables.need_same_host:
        return True
    if host in arr2.netloc:
        return True
    return False


def get_urls(parent, html, index):
    global HOST
    link_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", html)
    link_list = list(set(link_list))
    for url in link_list:
        if is_valid_url(url):
            if url.startswith("/") or url.startswith("#"):
                url = url_join(HOST, url)
            if url not in results:
                if not check_host(variables.host, url):
                    continue
                url = urllib.quote(url)
                url = urllib.unquote(url)
                if const.isDebug:
                    print "parent: " + parent + "\t" + "url: " + url
                results.append(url)
                if index < variables.level:
                    get_urls(url, get_html(url), index + 1)


if __name__ == '__main__':
    origin_url = raw_input("URL:")
    if not origin_url.startswith("http"):
        origin_url = "http://" + origin_url
    try:
        arr = urlparse.urlparse(origin_url)
        arrs = arr.netloc.split(".")
        if arrs.count >= 2:
            variables.host = arrs[len(arrs) - 2] + "." + arrs[len(arrs) - 1]
        else:
            variables.host = arr.netloc
    except:
        print "url not available"

    level = raw_input("LEVEL:")
    try:
        variables.level = int(level)
    except:
        variables.level = const.LEVEL

    get_urls(origin_url, get_html(origin_url), 1)
    do_write_file()
