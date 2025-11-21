# ライブラリのインポート
from bs4 import BeautifulSoup
import pandas as pd
import requests


def get_latest(
    soup: BeautifulSoup, base: str = "https://arxiv.org"
) -> tuple[list, list]:
    """
    arXiv から最新の論文を取得する関数

    Parameters
    ----------
    soup: BeautifulSoup
        スクレイピングしたデータ
    base: str="https://arxiv.org"
        arXiv のトップページ

    Returns
    ----------
    titles: list
        取得した論文のタイトルのリスト
    paper_urls: list
        取得した論文の URL のリスト
    """
    # 最新の日付の <dl> タグを取得
    latest_dl = soup.find("dl", {"id": "articles"})

    # 最新の日付の <dt> タグを取得
    latest_dt = latest_dl.find_all("dt")
    paper_urls = [
        base + item.find("a", href=True)["href"] for item in latest_dt
    ]

    # 最新の日付の <dd> タグを取得
    latest_dd = latest_dl.find_all("dd")
    titles = [
        item.find(
            "div", {"class": "list-title mathjax"}
        ).get_text(strip=True).replace("Title:", "") for item in latest_dd
    ]

    return titles, paper_urls


def get_abstract(soup: BeautifulSoup) -> str:
    """
    arXiv の論文の要旨を取得する関数

    Parameters
    ----------
    soup: BeautifulSoup
        スクレイピングしたデータ

    Returns
    ----------
    abstract: str
        論文の要旨
    """
    # 要旨を取得
    contents = soup.find("div", {"id": "content-inner"})
    abstract = contents.find(
        "blockquote", {"class": "abstract mathjax"}
    ).get_text(strip=True).replace("Abstract:", "")

    return abstract


def get_label(soup: BeautifulSoup) -> int:
    """
    arXiv の論文のラベルを取得する関数

    Parameters
    ----------
    soup: BeautifulSoup
        スクレイピングしたデータ

    Returns
    ----------
    label: int
        論文のラベル
    """
    # <tr> タグを取得
    contents = soup.find("div", {"id": "content-inner"})
    tables = contents.find("table", {"summary": "Additional metadata"})
    trs = tables.find_all("tr")

    # ラベルを取得
    tmp = [0, 0, 0]
    for tr in trs:
        # "Subjects" の部分のみ抽出
        if "Subjects" in tr.find("td", {"class": "tablecell label"}).text:
            subjects = tr.find("td", {"class": "tablecell subjects"}).text

            # ラベルの付与
            if "math.OC" in subjects:
                tmp[0] = 1
            if "cs.LG" in subjects:
                tmp[1] = 1
            if "quant-ph" in subjects:
                tmp[2] = 1

            # 抽出が終わったらループを抜ける
            break

    # ラベルを結合
    label = sum(tmp)

    return label


def get_info(url: str) -> tuple[str, int]:
    """
    arXiv の論文の要旨を取得する関数

    Parameters
    ----------
    url: str
        論文のページ

    Returns
    ----------
    abstract: str
        論文の要旨
    label: int
        論文のラベル
    """
    # 論文のページを取得
    sub_response = requests.get(url)
    sub_soup = BeautifulSoup(sub_response.text, "html.parser")

    # 要旨を取得
    abstract = get_abstract(sub_soup)

    # ラベルを取得
    label = get_label(sub_soup)

    return abstract, label


def search_arxiv(mode: str) -> pd.DataFrame:
    """
    arXiv から最新の論文情報を取得し、DataFrame にまとめる関数

    Parameters
    ----------
    mode: str
        最適化または機械学習または量子の分野

    Returns
    ----------
    df: pd.DataFrame
        最新の論文情報をまとめた DataFrame
    """
    # arXiv の URL
    if mode == "optimization":
        url = "https://arxiv.org/list/math.OC/recent?skip=0&show=2000"
    elif mode == "machine-learning":
        url = "https://arxiv.org/list/cs.LG/recent?skip=0&show=2000"
    elif mode == "quantum":
        url = "https://arxiv.org/list/quant-ph/recent?skip=0&show=2000"

    # ページの内容を取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 最新の論文情報を取得
    titles, paper_urls = get_latest(soup)

    # 各論文の情報を取得
    abstracts = []
    labels = []
    for url in paper_urls:
        abstract, label = get_info(url)
        abstracts.append(abstract)
        labels.append(label)

    # DataFrame にまとめる
    df = pd.DataFrame({
        "Title": titles,
        "Abstract": abstracts,
        "URL": paper_urls,
        "Label": labels
    })

    return df
