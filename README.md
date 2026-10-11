# risk-learning · 信贷风控建模学习仓库

风控算法方向的个人学习与项目仓库。主项目为「信贷违约预测与评分卡」。

## 数据来源

- **首选**：UCI Default of Credit Card Clients
  https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
- 本地路径：`data/raw/default of credit card clients.csv`（30001 行，23 个特征列 + 1 个标签列）
- 标签列：`default payment next month`（1 = 下月违约）

## 环境

- Python 3.14（`E:\python\python.exe`）
- 核心依赖：pandas / numpy / scikit-learn / lightgbm / scipy / statsmodels / matplotlib / seaborn / networkx

安装：

```bash
pip install -r requirements.txt
```

## 目录结构

```
risk-learning/
├── 01_clean/       数据清洗与缺失/异常值处理
├── 02_feature/     特征工程（分箱、WOE/IV、特征交叉、目标编码）
├── 03_model/       建模（LR 评分卡、LightGBM、模型融合、评估）
├── 04_fraud/       反欺诈专项（关系网络、图特征、团伙识别）
├── 05_report/      评估报告与可视化产出
├── 06_paper/       论文与文献笔记
├── 07_course/      课程内容 Python 复现
└── data/
    ├── raw/        原始数据（不进 git）
    └── processed/  中间产出
```

## 运行方式

```bash
# 1. 把原始数据放到 data/raw/
# 2. 依次运行
python 01_clean/clean_v1.py
python 02_feature/feature_v1.py
python 03_model/scorecard_v1.py
```

或直接用 Jupyter 打开对应目录下的 `.ipynb` 顺序执行。

## 项目进度

| 版本 | 内容 | 状态 |
|------|------|------|
| v1 | WOE → LR 评分卡 → KS/AUC 评估 | 待做（10/17） |
| v2 | LightGBM baseline + 5 折 CV，与 LR 对比 | 待做（10/20） |
| v3 | 采样策略 + 阈值优化 + 完整评估报告 | 待做（10/23） |

## 关键指标

| 模型 | AUC | KS | PSI |
|------|-----|----|----|
| LR 评分卡 | — | — | — |
| LightGBM | — | — | — |
| Stacking | — | — | — |

> UCI 数据集经验值参考：KS > 0.2、AUC > 0.6 即算正常水平。
