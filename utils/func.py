# ライブラリのインポート
import arxiv
import pandas as pd


def cats_to_label(categories: list) -> int:
    """
    カテゴリーリストをラベルに変換する関数

    Parameters
    ----------
    categories: list
        カテゴリーのリスト

    Returns
    ----------
    label: int
        ラベル化されたカテゴリー
    """
    # ラベルの初期化
    label = 0

    # 最適化系の論文は4
    if "math.OC" in categories:
        label += 4

    # 機械学習系の論文は2
    if "cs.LG" in categories:
        label += 2

    # 量子コンピュータ系の論文は1
    if "quant-ph" in categories:
        label += 1

    return label


def get_results(query: str, max_results: int = 500) -> list:
    """
    クエリに基づいて arXiv から論文を検索し, 結果を返す関数

    Parameters
    ----------
    query: str
        検索クエリ
    max_results: int = 500
        最大取得件数

    Returns
    ----------
    results: list
        検索結果のリスト
    """
    # Client オブジェクトの作成
    client = arxiv.Client()

    # 検索クエリの作成
    search = arxiv.Search(
        query=query, max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    # 検索の実行
    results = []
    for result in client.results(search):
        # タイトルを取得
        title = result.title

        # 要旨を取得
        summary = result.summary.replace("\n  ", " ").replace("\n  ", "  ")

        # 論文のURLを取得
        url = result.entry_id

        # カテゴリーを取得
        categories = result.categories
        label = cats_to_label(categories)

        # 結果を辞書形式で保存
        paper_info = {
            "Title": title,
            "Abstract": summary,
            "URL": url,
            "Label": label
        }
        results.append(paper_info)

    return results


def make_query(cat: str, date: str) -> str:
    """
    カテゴリーと日付を入れて検索クエリを作成する関数

    Parameters
    ----------
    cat: str
        カテゴリー
    date: str
        日付

    Returns
    ----------
    query: str
        作成された検索クエリ
    """
    # クエリの作成
    start = date + "0000"
    end = date + "2359"
    query = f"cat:{cat} AND submittedDate:[{start} TO {end}]"

    return query


def make_daily_df(date: str) -> pd.DataFrame:
    """
    日毎の論文情報をデータフレームにまとめる関数

    Parameters
    ----------
    date: str
        日付

    Returns
    ----------
    df: pd.DataFrame
        当日の論文情報をまとめたデータフレーム
    """
    # 検索カテゴリーのリスト
    categories = ["math.OC", "cs.LG", "quant-ph"]

    # 論文情報のリスト
    papers = []

    # 各カテゴリーごとに論文を取得
    for cat in categories:
        query = make_query(cat, date)
        results = get_results(query)
        papers.extend(results)

    # データフレームの作成
    df = pd.DataFrame(papers)
    df = df.drop_duplicates(subset=["Title"]).reset_index(drop=True)

    return df
