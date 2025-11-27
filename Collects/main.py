# ライブラリのインポート
from datetime import datetime, timedelta
import json

import pandas as pd
from tqdm import tqdm

from utils.func import make_daily_df

# Config ファイルを読み込む
cfg_path = "config.json"
with open(cfg_path, "r") as f:
    cfg = json.load(f)

# str 型日付リストを作成
start_date = datetime(
    cfg["start"]["year"], cfg["start"]["month"], cfg["start"]["day"]
)
end_date = datetime(
    cfg["end"]["year"], cfg["end"]["month"], cfg["end"]["day"]
)
date_list = [
    (start_date + timedelta(days=i)).strftime("%Y%m%d")
    for i in range((end_date - start_date).days + 1)
]

# 日毎のデータフレームを格納するリストを初期化
daily_dfs = []

# 各日のデータを収集して結合
with tqdm(range(len(date_list))) as date_pbar:
    for i in date_pbar:
        # 現在の日付を取得
        date = date_list[i]

        # 日毎のデータフレームを作成
        daily_df = make_daily_df(date)
        daily_dfs.append(daily_df)

        # 日毎のデータを保存
        daily_filename = f"../data/daily/any/{date}.csv"
        daily_df.to_csv(daily_filename, index=False)

        # キーワードに基づいてフィルタリング
        filtered_df = daily_df[
            daily_df["Abstract"].str.contains(
                "|".join(cfg["keywords"]), na=False
            )
        ]

        # フィルタリングしたデータを保存
        filtered_filename = f"../data/daily/interests/{date}.csv"
        filtered_df.to_csv(filtered_filename, index=False)

# 全データを結合
all_daily_df = pd.concat(daily_dfs, ignore_index=True)
all_daily_df = all_daily_df.drop_duplicates().reset_index(drop=True)

# 今までのデータを読み込み
all_data_path = "../data/all/arXiv.csv"
all_df = pd.read_csv(all_data_path)

# 新しいデータを結合して保存
combined_df = pd.concat([all_df, all_daily_df], ignore_index=True)
combined_df = combined_df.drop_duplicates().reset_index(drop=True)
combined_df.to_csv(all_data_path, index=False)
