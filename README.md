# 中山大学体育馆自动预约程序

本仓库整合了两套中大体育馆场地自动预约程序：

| 目录 | 说明 |
| --- | --- |
| [`sysugym_new/`](sysugym_new/) | ⭐ **新系统（推荐）**。对应学校改版后的现行预约网站（`gym.sysu.edu.cn`），支持 22:00 定时抢场、多场地优先级、邮件通知。 |
| [`legacy/`](legacy/) | 旧系统脚本（`bestonly.py`）。对应旧版预约网站，仅作存档，新版网站上线后可能已失效。 |

> ⚠️ 仅供个人学习与技术交流使用，请勿用于商业用途或任何违反学校规定的行为，使用后果自负。

---

## 新系统使用方法（`sysugym_new/`）

### 1. 安装依赖

```bash
cd sysugym_new
pip install -r requirements.txt
```

### 2. 下载 chromedriver

新系统通过 Selenium 驱动 Chrome 模拟登录、获取登录态 token，需要一个与本机 **Chrome 版本匹配** 的 chromedriver：

1. 打开 Chrome → 设置 → 关于 Chrome，记下版本号。
2. 到 <https://googlechromelabs.github.io/chrome-for-testing/> 下载对应版本的 `chromedriver-win32`。
3. 解压后，把整个 `chromedriver-win32/` 文件夹放到**仓库根目录**（与 `sysugym_new/` 同级），最终路径为 `chromedriver-win32/chromedriver.exe`。

> 仓库不再附带 `chromedriver.exe`：它体积大、与 Chrome 版本强绑定、更新很快，因此交由使用者按需下载。代码默认从 `../chromedriver-win32/chromedriver.exe`（即仓库根）读取，请勿改动目录层级。

### 3. 修改配置

编辑 [`sysugym_new/config.py`](sysugym_new/config.py)：

- `netiedid` / `password`：你的 NetID 账号与密码
- `target_starttime`：想预约的时间段，如 `["20:00", "21:00"]`
- `fields_order`：场地优先级（靠前者优先）
- `Description` / `VenueTypeId`：场地类型（默认「南校园新体育馆羽毛球场（学生）」）
- `way`：`"scheduled"` 定时抢场 / `"directly"` 立即订场
- 邮件通知：`mail`（是否发送）、`sender` / `receiver` / `smtpserver` / `password_email` 等

### 4. 运行

```bash
cd sysugym_new
python main.py
```

`scheduled` 模式会在约 21:50 启动、22:00 整开抢；命中空场后自动下单，并按配置发送邮件通知。

### 适用场地

适用于大部分可自主选择场地的预定，例如：

- 南校园新体育馆羽毛球场 / 乒乓球室
- 北校园羽毛球场
- 东校园羽毛球场
- 珠海校区新体育馆网球场 / 羽毛球场 / 乒乓球室

---

## 旧系统（`legacy/`）

旧版预约网站对应的单文件脚本，保留作存档。使用方法见 [`legacy/readme.txt`](legacy/readme.txt)。学校切换到新版网站后，旧脚本可能已不可用。

---

## License

[MIT](LICENSE) © 2025 eternalstargalaxy
