# ライブラリのインポート
from datetime import datetime

import pandas as pd

from utils.func import search_arxiv

# 最適化のデータを保存
opt_df = search_arxiv("optimization")

# 機械学習のデータを保存
ml_df = search_arxiv("machine-learning")

# 量子のデータを保存
quantum_df = search_arxiv("quantum")

# 3つのデータを結合し, 重複を削除
all_df = pd.concat([opt_df, ml_df, quantum_df], ignore_index=True)
all_df = all_df.drop_duplicates(subset=["Title", "Abstract"])

# ファイル名を作成して CSV ファイルに保存
today = str(datetime.today().date()).replace("-", "_")
filename = f"../data/daily/any/{today}.csv"
all_df.to_csv(filename, index=False)

# 興味のあるキーワードをリスト化
keywords = [
    "quantum machine learning", "Quantum Machine Learning", "QML",
    "quantum neural network", "Quantum Neural Network", "QNN",
    "quantum reservoir computing", "Quantum Reservoir Computing",
    "QAOA", "Reinforcement Learning", "reinforcement learning",
    "Graph Neural Network", "graph neural network", "GNN",
    "Point Cloud", "point cloud"
]

# キーワードに基づいてフィルタリング
filtered_df = all_df[
    all_df["Abstract"].str.contains("|".join(keywords), na=False)
]

# フィルタリングしたデータを保存
filtered_filename = f"../data/daily/interests/{today}.csv"
filtered_df.to_csv(filtered_filename, index=False)

# 今までのデータをすべて結合
archive_path = "../data/all/arXiv.csv"
archive_df = pd.read_csv(archive_path)
combined_df = pd.concat([archive_df, all_df], ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=["Title", "Abstract"])
combined_df.to_csv(archive_path, index=False)
