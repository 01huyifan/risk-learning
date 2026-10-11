"""
01_clean/clean_v1.py — 数据清洗流水线

对应排期：10/17 项目 v1 的预处理部分（复用 9 月 utils.py 的写法）
目标：读取原始数据 → 缺失处理 → 异常值 → 类型规整 → 落盘到 data/processed/

运行：
    python 01_clean/clean_v1.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

# ---------- 路径 ----------
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "default of credit card clients.csv"
OUT = ROOT / "data" / "processed" / "clean.csv"

TARGET = "default payment next month"


def load_raw(path: Path) -> pd.DataFrame:
    """读取原始数据。UCI 这份文件的表头在第 1 行、id 列在第 0 列。"""
    df = pd.read_csv(path, header=1)
    df = df.rename(columns={df.columns[0]: "ID", TARGET: "target"})
    return df


def report_missing(df: pd.DataFrame, name: str = "raw") -> None:
    """打印缺失概览——不是每个数据集都缺，但这一步必须有。"""
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if miss.empty:
        print(f"[{name}] 无缺失值")
    else:
        print(f"[{name}] 缺失列：\n{miss}")


def fix_unknown_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    UCI 数据集的已知坑：
      EDUCATION: 0 / 5 / 6 是未定义值（文档只定义 1=研究生 2=本科 3=高中 4=其他）
      MARRIAGE : 0 是未定义值（文档只定义 1=已婚 2=单身 3=其他）
    处理方式：归到「其他」，不要随便删。
    """
    df = df.copy()
    df["EDUCATION"] = df["EDUCATION"].where(df["EDUCATION"].isin([1, 2, 3, 4]), 4)
    df["MARRIAGE"] = df["MARRIAGE"].where(df["MARRIAGE"].isin([1, 2, 3]), 3)
    return df


def fix_pay_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    PAY_0..PAY_6 的还款状态：文档里 -2=-2 个月、-1=按时还款、0=循环信用
    实际数据里有 -2/-1/0/1..9，其中 -2/-1 在建模时通常合并到一个「正常」档。
    这里只做合规化：把小于 -1 的值统一成 -1（保持有序，不引入假类别）。
    """
    df = df.copy()
    pay_cols = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
    for c in pay_cols:
        df[c] = df[c].clip(lower=-1)
    return df


def detect_outlier(df: pd.DataFrame, cols: list[str], k: float = 3.0) -> pd.DataFrame:
    """
    用 IQR 法标记异常值（默认 3 倍 IQR 的宽松口径）。
    ★ 风控里金额类字段的「异常值」往往就是真实的坏样本，不要直接删——
      这里只打标记，是否处理交给下游决定。
    """
    df = df.copy()
    for c in cols:
        q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - k * iqr, q3 + k * iqr
        df[f"{c}_is_outlier"] = ((df[c] < lo) | (df[c] > hi)).astype(int)
    return df


def main() -> None:
    print("=" * 60)
    df = load_raw(RAW)
    print(f"原始数据：{df.shape[0]} 行 × {df.shape[1]} 列")
    report_missing(df, "raw")

    print("\n已知问题类别分布：")
    print("  EDUCATION:", df["EDUCATION"].value_counts().to_dict())
    print("  MARRIAGE :", df["MARRIAGE"].value_counts().to_dict())

    df = fix_unknown_categories(df)
    df = fix_pay_status(df)

    bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]
    amt_cols = [f"PAY_AMT{i}" for i in range(1, 7)]
    df = detect_outlier(df, bill_cols + amt_cols)

    print(f"\n清洗后：{df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"标签分布：{df['target'].value_counts().to_dict()}"
          f"  违约率 {df['target'].mean():.4f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\n已输出 → {OUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
