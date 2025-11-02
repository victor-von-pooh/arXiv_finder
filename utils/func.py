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
            "div", class_="list-title mathjax"
        ).get_text(strip=True).replace("Title:", "") for item in latest_dd
    ]

    return titles, paper_urls


def get_abstract(url: str) -> str:
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
    """
    # 論文のページを取得
    sub_response = requests.get(url)
    sub_soup = BeautifulSoup(sub_response.text, "html.parser")

    # 要旨を取得
    contents = sub_soup.find("div", {"id": "content-inner"})
    abstract = contents.find(
        "blockquote", class_="abstract mathjax"
    ).get_text(strip=True).replace("Abstract:", "")

    return abstract


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

    # 各論文の要旨を取得
    abstracts = [get_abstract(url) for url in paper_urls]

    # DataFrame にまとめる
    df = pd.DataFrame({
        "Title": titles,
        "Abstract": abstracts,
        "URL": paper_urls
    })

    return df
