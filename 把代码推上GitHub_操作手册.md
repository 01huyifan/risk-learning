# 把代码推上 GitHub · 操作手册

> 这份文档是**独立**的，不需要翻聊天记录。
> 全程两步：**装 Git → 双击一个脚本**。不用敲命令。

---

## 一、现在到底差什么

| 步骤 | 状态 | 说明 |
|---|---|---|
| 1. GitHub 账号 | ✅ 已完成 | 用户名 `01huyifan` |
| 2. 建立远程仓库 | ✅ 已完成 | 仓库名 `risk-learning`，Public |
| 3. 本地代码提交 | ✅ 已完成 | 本地已有 5 个提交（commit） |
| 4. 本地关联远程 | ✅ 已完成 | `origin` 已指向你的仓库 |
| 5. 电脑上装 Git | ✅ 已完成 | Git 2.56.0.2，已装并进 PATH |
| 6. 推送（push） | ✅ **已完成** | 30 个文件已上传，`main -> main` |

> ### 🎉 全部完成（2026-10-12 17:39）
> 仓库地址：**https://github.com/01huyifan/risk-learning**
> 远端 `main` 上的 commit 是 `2037175`，与本地**完全一致**。
>
> **这份文档留着当参考** —— 以后遇到类似问题（换电脑、重装系统、报错），
> 可以直接翻第三节「双击脚本」和第四节「失败怎么办」。

---

## 二、第一步：装 Git（约 3 分钟）

### 1. 找到安装包

**桌面上已经放好了**：

```
Git-2.56.0.2-64-bit.exe
```

这是 Git 官方安装包，从国内镜像站（npmmirror）下的，63.7 MB。
如果双击提示"Windows 已保护你的电脑" → 点 **`更多信息`** → **`仍要运行`**（这是正常的，因为是自己下载的安装包）。

### 2. 一路点 `Next`

安装向导大概有 10 屏，**全部保持默认，一直点 `Next`** 就行。只有一处要留意：

> **「Adjusting your PATH environment」** 这一屏
> 默认选中的是中间的 **`Git from the command line and also from 3rd-party software`**
> → **保持这个不要动**。千万不要选最上面的 `Use Git from Git Bash only`。
> （这一屏决定了 `.bat` 脚本能不能找到 git）

其他屏（编辑器、换行符、终端类型、额外选项）默认都对，直接过。

### 3. 点 `Install` → 等进度条 → 点 `Finish`

### 4. ⚠️ 装完后：关掉所有已开着的黑窗口

因为 Windows 要重新加载 PATH，**之前打开的 cmd / Git Bash 窗口不会知道 git 装好了**。
重新打开才生效。

### 5. 验证装好了没有

按 `Win` 键，搜 **`Git Bash`**。
- 搜出来**能打开的软件**（不是网页结果）→ 装好了
- 或者：开一个新的黑窗口，敲 `git --version`，能打印版本号就对了

---

## 三、第二步：双击脚本推送（约 1 分钟）

回到 `C:\Users\hyf\Desktop\risk-learning` 文件夹，**双击**：

```
push-to-github.bat
```

**会发生什么：**

1. 弹出黑窗口，显示 `Git found. Starting upload ...`
2. **第一次推送会弹出一个登录窗口**（Git Credential Manager）
   - 一般会开浏览器让你登录 GitHub → 登录并点 `Authorize`
   - 或者在窗口里填：用户名 `01huyifan`，密码用 **Token**（见第五节）
3. 等它传输，结束后窗口会停住显示 `请按任意键继续`

**成功的标志：** 窗口里有一行带 `main`（例如 `main -> main`），**并且没有红色报错**。

**然后打开验证：**

```
https://github.com/01huyifan/risk-learning
```

能看到 `README.md`、`01_clean`、`02_feature`、`03_model` 这些文件和文件夹 → **大功告成。**

---

## 四、万一双击脚本失败

### 情况 A：窗口一闪就没了

说明脚本本身没跑起来。改用**手动版**（下面第五节）。

### 情况 B：窗口报 `Git was NOT found`

说明 Git 没装成功，或者 PATH 没生效。回第二步，重点检查：
- 安装时那一屏有没有选成 `Use Git from Git Bash only`
- 装完后有没有**关掉旧窗口再重开**

### 情况 C：报红色错误（如 `Authentication failed`）

- `Authentication failed` → Token 不对或过期 → 重新生成（第五节）
- `Support for password authentication was removed` → 你填的是账号密码，必须填 Token
- 卡住几十分钟不动 → 网络问题 → 开加速器重试，或告诉我转 Gitee

---

## 五、手动版（Git Bash）

只有双击法失败时才需要。

### 1. 打开 Git Bash

- 文件资源管理器进到 `C:\Users\hyf\Desktop\risk-learning`
- 文件夹**空白处右键** → **`Open Git Bash here`**
- 黑窗口弹出，已经站在正确目录

**验证位置：** 敲 `pwd`，应显示 `/c/Users/hyf/Desktop/risk-learning`

### 2. 生成 Token（登录用）

GitHub 早就不允许用账号密码推代码了，要用 Token 代替：

1. 浏览器打开 `github.com/settings/tokens`
2. `Generate new token` → **`Generate new token (classic)`**
3. **Note** 随便填，如 `risk-learning laptop`
4. **Expiration** 选 `90 days`
5. 勾最上面那个 **`repo`**（勾大框，子项自动全选）
6. 拉到底点绿色 **`Generate token`**
7. ⚠️ 出现一串 `ghp_xxxx...` → **立刻复制**，**只显示这一次**
8. ⚠️ **不要发给任何人**，自己留着

### 3. 推送

```bash
git push origin main
```

问 Username → `01huyifan`；问 Password → 粘那串 `ghp_...`

---

## 六、成功之后：以后每天怎么用

以后写完代码，三条命令（或者直接双击 `push-to-github.bat`）：

```bash
cd "C:/Users/hyf/Desktop/risk-learning"
git add -A
git commit -m "今天写了什么就填这里"
git push
```

第一次之后就不再问账号密码了。

---

## 附：这个项目是什么

`risk-learning` 是你的风控算法学习路线的**代码仓库**：

| 目录 | 内容 |
|---|---|
| `01_clean/` | 数据清洗（脏数据修正） |
| `02_feature/` | 特征工程（WOE、IV、分箱） |
| `03_model/` | 建模（逻辑回归评分卡、LightGBM） |
| `04_fraud/` | 反欺诈 |
| `05_report/` | 报告 |
| `06_paper/` | 论文 |
| `07_course/` | 课程作业 |
| `data/` | 数据（**不上传**，已被 `.gitignore` 挡住） |

**已经跑通的结果**（重跑脚本可复现）：

- 清洗后：30000 行 × 37 列，违约率 **0.2212**
- IV 最高变量：**PAY_0 = 0.873**
- 逻辑回归评分卡：**AUC 0.7639 / KS 0.4178**
- LightGBM：AUC 0.7681（比 LR 只高 0.004，判为噪声，故选可解释性更好的 LR）

---

**卡住就截图，不用自己找原因。**
