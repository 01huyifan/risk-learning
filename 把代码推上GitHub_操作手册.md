# 明天照这个做：把代码推上 GitHub

> 这份文档是**独立**的，不需要翻之前的聊天记录。
> 现在进度：账号有、仓库有、代码在本地、远端已连好。
> **只剩"推上去"这一个动作。**

---

## ⭐ 最省事的办法（推荐先试这个）

**不用开 Git Bash，不用敲命令。**

在这个文件夹里找到 **`push-to-github.bat`**，**双击它**。

- 会弹出一个黑窗口，自动开始推送
- 如果弹出登录窗口 → 用 GitHub 账号登录（会开浏览器让你授权，照着点）
- 跑完后窗口会停住 **`请按任意键继续`**，**先别关**，看清楚上面写的是成功还是报错
- **成功了** → 打开 `https://github.com/01huyifan/risk-learning` 能看到文件，就完事了
- **报错了** → 截图发出来

> 如果双击后窗口一闪就没了：说明 git 没在系统 PATH 里，
> 那就走下面第三节「打开 Git Bash」的办法。

**下面第三节往后是手动版，双击法失败时再看。**

---

## 一、先搞清楚：现在到底差什么

| 步骤 | 状态 | 说明 |
|---|---|---|
| 1. GitHub 账号 | ✅ 已完成 | 用户名 `01huyifan` |
| 2. 建立远程仓库 | ✅ 已完成 | 仓库名 `risk-learning`，Public |
| 3. 本地代码提交 | ✅ 已完成 | 本地有 3 个提交（commit） |
| 4. 本地关联远程 | ✅ 已完成 | `origin` 已指向你的仓库 |
| 5. **推送（push）** | ❌ **就差这一步** | 之前失败，因为网络慢 + 没配好登录凭据 |

**所以明天只做第 5 步。** 不用重新建仓库，不用重新提交代码。

---

## 二、开工前先解决网络（重要）

你的网络到 GitHub 是「能连上但传不动」，直接推会卡死。

**先做这个二选一：**

- **A. 有加速器 / 梯子** → 打开它，保持开着，再做第三步
- **B. 没有加速器** → **别硬试了**，直接告诉 AI「我没有加速器，转 Gitee」，
  换国内站（码云），十分钟搞定，简历上一样能点开

---

## 三、打开 Git Bash（命令行窗口）

**方法一（推荐，最省事）：**

1. 打开**文件资源管理器**（任务栏那个黄色文件夹图标）
2. 在**地址栏**输入下面这行，回车：
   ```
   C:\Users\hyf\Desktop\risk-learning
   ```
3. 现在你就在 `risk-learning` 文件夹里了
4. 在文件夹**空白处**（不要点在文件上）**右键**
5. 菜单里点 **`Open Git Bash here`**（中文版可能写「Git Bash Here」）
6. 黑窗口弹出 —— **而且已经自动站在正确的位置了**

**方法二（搜索打开）：**

1. 按 `Win` 键，搜 `Git Bash`
2. 搜索结果里**双击左边那条 `git bash`**（不是右边的网页介绍）
3. 窗口出来后，手动进去：
   ```bash
   cd "C:/Users/hyf/Desktop/risk-learning"
   ```

**怎么确认自己站对了位置？** 敲这一句回车：

```bash
pwd
```

应该显示：
```
/c/Users/hyf/Desktop/risk-learning
```

只要这行对，就可以往下走。

---

## 四、生成新的 Token（登录用）

**为什么要 Token？** GitHub 从 2021 年起就不允许用账号密码推代码了，必须用 Token 代替密码。

1. 浏览器打开：`github.com/settings/tokens`
2. 点 **`Generate new token`** → 选 **`Generate new token (classic)`**
3. **Note** 栏随便填，例如 `risk-learning laptop`
4. **Expiration** 选 **`90 days`**
5. 权限列表里，**勾最上面那个 `repo`**（勾大框，子项会自动全勾）
6. 拉到最底，点绿色 **`Generate token`**
7. ⚠️ 页面会显示一串 `ghp_xxxxxxxx...` —— **立刻复制保存**
   - **这串只显示这一次，刷新就没了**
   - ⚠️ **这次不要发给 AI**，自己留着（上次发出去的那个已经作废了）

---

## 五、推送代码

在 Git Bash 窗口里，敲这一句，回车：

```bash
git push origin main
```

**接下来会发生的事：**

1. 弹出一个小窗口（Git Credential Manager）要你登录
2. 如果它问 **Username** → 填 `01huyifan`
3. 如果它问 **Password / Token** → **粘贴刚才那串 `ghp_...`**
4. 等它跑

**成功的标志（会看到类似这样的输出）：**

```
Enumerating objects: ...
Writing objects: 100% (...)
To https://github.com/01huyifan/risk-learning.git
 * [new branch]      main -> main
```

**看到 `main -> main` 就是成功了。**

---

## 六、验证

浏览器打开你的仓库地址：

```
https://github.com/01huyifan/risk-learning
```

**能看到文件列表（README.md、01_clean 文件夹等）就说明全通了。**

---

## 七、常见报错对照

| 报错 | 意思 | 怎么办 |
|---|---|---|
| 卡住不动、几十分钟没输出 | 网络传不动 | 开加速器重试；或转 Gitee |
| `Authentication failed` | Token 不对或过期 | 重新生成 Token，或者去掉多余空格 |
| `Support for password authentication was removed` | 你填的是账号密码，不是 Token | 必须填 `ghp_...` 那串 |
| `remote origin already exists` | 远端已连过了 | 不用管，直接继续 push |
| `failed to push some refs` | 远端有你没有的东西 | 截图给 AI 看 |
| 弹窗一直不出现 | 凭据管理器没启动 | 在窗口里手动敲用户名和 Token |

**任何一步卡住 → 直接截图发给 AI，不用自己琢磨。**

---

## 八、成功之后：以后每天怎么用

**每天写完代码，只要三条命令：**

```bash
cd "C:/Users/hyf/Desktop/risk-learning"
git add -A
git commit -m "写了什么就填这里"
git push
```

**第一次之后，push 就不再问账号密码了**（凭据管理器会记住）。

---

## 附：这个项目是什么

`risk-learning` 是你风控算法学习路线的**代码仓库**，三个核心目录：

- `01_clean/` —— 数据清洗（脏数据怎么修）
- `02_feature/` —— 特征工程（WOE、IV、分箱）
- `03_model/` —— 模型建模（逻辑回归评分卡、LightGBM）

**其他目录**：`04_fraud`（反欺诈）、`05_report`（报告）、`06_paper`（论文）、`07_course`（课程作业）、`data/`（数据，不上传）

**已经跑通的结果**（重新运行脚本可以得到同样结果）：

- 清洗后：30000 行 × 37 列，违约率 0.2212
- IV 最高变量：PAY_0 = 0.873
- 逻辑回归评分卡：AUC 0.7639 / KS 0.4178

---

**卡住就截图，不用自己找原因。**
