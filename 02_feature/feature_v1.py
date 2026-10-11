"""
02_feature/feature_v1.py — 特征工程流水线

对应排期：10/15 基础版分箱 + 11/1 进阶（特征交叉、目标编码、决策树最优分箱）
本文档实现「基础版」：卡方分箱 → WOE/IV → 单调性检验 → 输出建模用宽表

运行：
    python 02_feature/feature_v1.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "clean.csv"
OUT = ROOT / "data" / "processed" / "features.csv"
IV_TABLE = ROOT / "05_report" / "iv_table.csv"

# 进入分箱的连续 / 有序变量
NUM_COLS = ["LIMIT_BAL", "AGE",
            "BILL_AMT1", "BILL_AMT2", "BILL_AMT3",
            "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
            "PAY_AMT1", "PAY_AMT2", "PAY_AMT3",
            "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
# 类别变量
CAT_COLS = ["SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]

MIN_BIN_PCT = 0.05   # 每箱最少样本占比
MAX_BINS = 5         # 最多箱数


# ---------------- 分箱 ----------------
def _initial_bins(s: pd.Series, max_bins: int = MAX_BINS) -> list:
    """用分位数切初始分位点（卡方分箱的起点）。"""
    qs = np.linspace(0, 1, max_bins + 1)[1:-1]
    edges = sorted(set(np.quantile(s, qs)))
    return [-np.inf] + list(edges) + [np.inf]


def _bin_stats(df: pd.DataFrame, col: str, edges: list) -> pd.DataFrame:
    """
    统计每一箱的好坏样本数与 WOE / IV 分量。

    ★ WOE 方向约定（标准评分卡口径）：
        WOE = ln(坏占比 / 好占比) = ln(bad_pct / good_pct)
      这样「坏客户占比越高」的箱 WOE 越大（正），配上 LR 的正系数，
      分数越高 → 越坏，符合评分卡的直觉与监管可解释性要求。
      （如果写成 ln(good/bad)，所有系数会翻成负数，虽然预测等价，
        但系数不可直接解释，评分卡报告会被打回。）
    """
    tmp = df[[col, "target"]].copy()
    tmp["bin"] = pd.cut(tmp[col], bins=edges, include_lowest=True, duplicates="drop")
    g = tmp.groupby("bin", observed=True)["target"].agg(["count", "sum"])
    g.columns = ["total", "bad"]
    g["good"] = g["total"] - g["bad"]
    # 防止除零
    g["bad"] = g["bad"].clip(lower=0.5)
    g["good"] = g["good"].clip(lower=0.5)
    total_bad, total_good = g["bad"].sum(), g["good"].sum()
    g["bad_pct"] = g["bad"] / total_bad
    g["good_pct"] = g["good"] / total_good
    g["woe"] = np.log(g["bad_pct"] / g["good_pct"])
    g["iv"] = (g["bad_pct"] - g["good_pct"]) * g["woe"]
    return g


def chi_merge(df: pd.DataFrame, col: str, max_bins: int = MAX_BINS) -> list:
    """
    卡方分箱（ChiMerge，自底向上合并相邻区间）。
    ★ 这是 11/25 非参 U3 的核心算法，第一遍必须自己写。
    合并准则：相邻两箱卡方值最小且低于阈值 → 合并。
    """
    edges = _initial_bins(df[col], max_bins)
    while len(edges) - 1 > 2:
        stats = _bin_stats(df, col, edges)
        if len(stats) <= 2:
            break
        # 相邻箱两两卡方
        chi_list = []
        counts = stats[["good", "bad"]].values
        for i in range(len(counts) - 1):
            table = np.array([counts[i], counts[i + 1]])
            try:
                chi2, _, _, _ = chi2_contingency(table)
            except Exception:
                chi2 = 0.0
            chi_list.append(chi2)
        # 合并卡方最小的那一对（即两箱分布最像）
        idx = int(np.argmin(chi_list))
        edges.pop(idx + 1)
        # 样本占比过小的箱也合并
        stats2 = _bin_stats(df, col, edges)
        small = stats2[stats2["total"] / len(df) < MIN_BIN_PCT]
        if len(small) > 0 and len(edges) - 1 > 2:
            j = stats2.index.get_loc(small.index[0])
            edges.pop(min(j, len(edges) - 2))
        if len(edges) - 1 <= 2:
            break
    return edges


def woe_iv(df: pd.DataFrame, col: str, edges: list) -> tuple:
    """按给定分箱算 WOE 映射表与总 IV。"""
    stats = _bin_stats(df, col, edges)
    woe_map = {interval: w for interval, w in zip(stats.index, stats["woe"])}
    iv = stats["iv"].sum()
    return woe_map, iv, stats


def monotonic_check(stats: pd.DataFrame) -> bool:
    """检查 WOE 是否单调——不单调的箱子业务上不好解释，面试常问。"""
    w = stats["woe"].values
    d = np.diff(w)
    return bool(np.all(d >= 0)) or bool(np.all(d <= 0))


# ---------------- 主流程 ----------------
def main() -> None:
    print("=" * 60)
    df = pd.read_csv(IN)
    print(f"输入：{df.shape[0]} 行 × {df.shape[1]} 列")

    rows = []
    feature_df = df[["target"]].copy()

    print("\n【数值变量 · 卡方分箱 → WOE】")
    for c in NUM_COLS:
        edges = chi_merge(df, c)
        woe_map, iv, stats = woe_iv(df, c, edges)
        mono = monotonic_check(stats)
        feature_df[f"{c}_woe"] = pd.cut(df[c], bins=edges, include_lowest=True,
                                        duplicates="drop").map(woe_map).astype(float)
        rows.append({"feature": c, "iv": iv, "bins": len(stats),
                     "monotonic": mono, "edges": [round(e, 1) for e in edges[1:-1]]})
        flag = "OK " if mono else "!! 非单调"
        print(f"  {c:<12} IV={iv:6.4f}  箱数={len(stats)}  {flag}")

    print("\n【类别变量 · 直接算 WOE】")
    for c in CAT_COLS:
        edges = [df[c].min() - 1] + list(df[c].sort_values().unique()) + [df[c].max() + 1]
        woe_map, iv, stats = woe_iv(df, c, edges)
        mono = monotonic_check(stats)
        feature_df[f"{c}_woe"] = df[c].map(
            {interval: w for interval, w in zip(stats.index, stats["woe"])}
        ).fillna(0.0)
        # 类别变量用区间不好映射，改成按原值映射（WOE 方向同上：ln(bad_pct/good_pct)）
        tmp = df[[c, "target"]].copy()
        tmp = tmp.groupby(c)["target"].agg(["count", "sum"])
        tmp.columns = ["total", "bad"]
        tmp["good"] = tmp["total"] - tmp["bad"]
        tmp["bad"] = tmp["bad"].clip(lower=0.5)
        tmp["good"] = tmp["good"].clip(lower=0.5)
        tmp["woe"] = np.log((tmp["bad"] / tmp["bad"].sum()) / (tmp["good"] / tmp["good"].sum()))
        tmp["iv"] = ((tmp["bad"] / tmp["bad"].sum()) - (tmp["good"] / tmp["good"].sum())) * tmp["woe"]
        iv = tmp["iv"].sum()
        feature_df[f"{c}_woe"] = df[c].map(tmp["woe"]).fillna(0.0)
        rows.append({"feature": c, "iv": iv, "bins": len(tmp),
                     "monotonic": None, "edges": list(tmp.index)})
        print(f"  {c:<12} IV={iv:6.4f}  类别数={len(tmp)}")

    iv_df = pd.DataFrame(rows).sort_values("iv", ascending=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    IV_TABLE.parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(OUT, index=False)
    iv_df.to_csv(IV_TABLE, index=False)

    print(f"\n【IV 排名 Top 10】")
    print(iv_df.head(10).to_string(index=False))
    print(f"\nIV 筛选参考：>0.3 强，0.1–0.3 中，0.02–0.1 弱，<0.02 基本无用")
    print(f"\n已输出 → {OUT}")
    print(f"已输出 → {IV_TABLE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
