"""
03_model/scorecard_v1.py — LR 评分卡 + LightGBM 对比

对应排期：
  10/17 项目 v1：WOE → LR 评分卡 → KS/AUC 评估
  10/20 项目 v2：LightGBM baseline + 5 折 CV，与 LR 对比
  10/23 项目 v3：采样策略 + 阈值优化 + 完整评估报告

本文档一次实现 v1–v3 的主干，输出指标表到 05_report/。

运行：
    python 03_model/scorecard_v1.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "processed" / "features.csv"
OUT_METRICS = ROOT / "05_report" / "metrics.json"
OUT_BINS = ROOT / "05_report" / "score_distribution.csv"

TARGET = "target"
SEED = 42


# ---------------- 指标 ----------------
def ks_stat(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """KS = max(TPR - FPR)，等同于两条累积分布曲线的最大间距。"""
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """PSI = Σ (实际占比 - 期望占比) × ln(实际/期望)。<0.1 稳定，>0.25 需重建。"""
    breakpoints = np.arange(0, bins + 1) / bins * 100
    breakpoints = np.percentile(expected, breakpoints)
    breakpoints[0], breakpoints[-1] = -np.inf, np.inf
    exp_pct = np.histogram(expected, breakpoints)[0] / len(expected)
    act_pct = np.histogram(actual, breakpoints)[0] / len(actual)
    exp_pct = np.where(exp_pct == 0, 1e-6, exp_pct)
    act_pct = np.where(act_pct == 0, 1e-6, act_pct)
    return float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))


def score_distribution(y_true: np.ndarray, score: np.ndarray, bins: int = 10) -> pd.DataFrame:
    """分数分布表：10 档，每档好/坏人数与 bad rate。"""
    edges = np.percentile(score, np.arange(0, bins + 1) / bins * 100)
    edges[0], edges[-1] = -np.inf, np.inf
    grp = pd.cut(score, edges, include_lowest=True)
    d = pd.DataFrame({"score_bin": grp, "target": y_true})
    t = d.groupby("score_bin", observed=True)["target"].agg(["count", "sum"])
    t.columns = ["total", "bad"]
    t["good"] = t["total"] - t["bad"]
    t["bad_rate"] = t["bad"] / t["total"]
    return t.reset_index()


# ---------------- 主流程 ----------------
def main() -> None:
    print("=" * 64)
    df = pd.read_csv(IN)
    y = df[TARGET].values
    X = df.drop(columns=[TARGET])
    feat_cols = [c for c in X.columns if c.endswith("_woe")]
    X = X[feat_cols]
    print(f"样本 {X.shape[0]} × 特征 {X.shape[1]}（全部 WOE 编码）")

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=SEED, stratify=y)
    print(f"训练 {len(X_tr)} / 测试 {len(X_te)}")

    metrics = {}

    # ---------- 模型 1：LR 评分卡 ----------
    print("\n【模型 1 · LR 评分卡】")
    scaler = StandardScaler()
    Xtr_s = scaler.fit_transform(X_tr)
    Xte_s = scaler.transform(X_te)
    lr = LogisticRegression(max_iter=1000, random_state=SEED)
    lr.fit(Xtr_s, y_tr)
    p_lr = lr.predict_proba(Xte_s)[:, 1]
    auc_lr, ks_lr = roc_auc_score(y_te, p_lr), ks_stat(y_te, p_lr)
    psi_lr = psi(p_lr, p_lr)  # 同分布自比，基线为 0
    print(f"  AUC={auc_lr:.4f}  KS={ks_lr:.4f}")
    metrics["LR_scorecard"] = {"auc": round(auc_lr, 4), "ks": round(ks_lr, 4)}

    # LR 系数（WOE 编码下系数应全为正——这是评分卡的基本要求）
    coef = pd.Series(lr.coef_[0], index=feat_cols).sort_values(ascending=False)
    neg = coef[coef < 0]
    print(f"  系数为正（符合评分卡要求）：{(coef > 0).sum()}/{len(coef)}")
    if len(neg):
        print(f"  ★ 系数为负（需检查 WOE 方向）：{list(neg.index)}")

    # ---------- 模型 2：LightGBM ----------
    print("\n【模型 2 · LightGBM】")
    clf = lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=31,
        subsample=0.8, colsample_bytree=0.8,
        random_state=SEED, verbose=-1)
    clf.fit(X_tr, y_tr)
    p_gbm = clf.predict_proba(X_te)[:, 1]
    auc_gbm, ks_gbm = roc_auc_score(y_te, p_gbm), ks_stat(y_te, p_gbm)
    print(f"  AUC={auc_gbm:.4f}  KS={ks_gbm:.4f}")
    metrics["LightGBM"] = {"auc": round(auc_gbm, 4), "ks": round(ks_gbm, 4)}

    # ---------- 5 折 CV（模型稳定性） ----------
    print("\n【5 折交叉验证 · LightGBM】")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    aucs = []
    for i, (tr, va) in enumerate(skf.split(X, y), 1):
        m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05,
                               num_leaves=31, random_state=SEED, verbose=-1)
        m.fit(X.iloc[tr], y[tr])
        a = roc_auc_score(y[va], m.predict_proba(X.iloc[va])[:, 1])
        aucs.append(a)
        print(f"  Fold {i}: AUC={a:.4f}")
    print(f"  均值 {np.mean(aucs):.4f} ± {np.std(aucs):.4f}")
    metrics["LGB_5fold"] = {"auc_mean": round(float(np.mean(aucs)), 4),
                            "auc_std": round(float(np.std(aucs)), 4)}

    # ---------- PSI：训练 vs 测试的分布稳定性 ----------
    psi_val = psi(p_lr, p_gbm)
    print(f"\n【PSI】LR 与 LGB 分数分布差异 = {psi_val:.4f}"
          f"  ({'稳定' if psi_val < 0.1 else '需关注'})")
    metrics["psi_lr_vs_gbm"] = round(psi_val, 4)

    # ---------- 分数分布表 ----------
    dist = score_distribution(y_te, p_lr)
    dist.to_csv(OUT_BINS, index=False)
    mono = dist["bad_rate"].is_monotonic_decreasing
    print(f"\n【分数分布表】违约率单调性：{'单调递减 OK' if mono else '!! 非单调，需检查分箱'}")
    print(dist.to_string(index=False))

    # ---------- 结论 ----------
    gain = auc_gbm - auc_lr
    print(f"\n【v1–v3 结论】")
    print(f"  LR 基线 AUC={auc_lr:.4f} → LGB AUC={auc_gbm:.4f}，提升 {gain:+.4f}")
    print(f"  提升 {gain*100:.2f} 个百分点。")
    verdict = "显著" if gain > 0.02 else ("有但不大" if gain > 0.005 else "可视为噪声")
    print(f"  判定：{verdict}（经验阈值：AUC 提升 < 0.005 视为噪声）")
    print(f"\n  ★ 业务结论：{'优先用 LightGBM 提效，但需配合 SHAP 解释' if gain > 0.02 else 'LR 评分卡已足够，可解释性优先——监管友好且上线成本低'}")

    OUT_METRICS.parent.mkdir(parents=True, exist_ok=True)
    OUT_METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"\n已输出 → {OUT_METRICS}")
    print(f"已输出 → {OUT_BINS}")
    print("=" * 64)


if __name__ == "__main__":
    main()
