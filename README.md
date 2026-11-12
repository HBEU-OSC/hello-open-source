# hello-open-source

> 湖北工程学院开源社团 · 第一个协作仓库
> 一个会自动对战的「三蛇争霸」游戏，也是社团成员练习开源协作的第一站。

本仓库有两个用途：

1. **练习开源协作**：如果你是第一次接触 GitHub，这里是提交你第一个 Pull Request 的安全起点（新手请先读 [CONTRIBUTING.md](CONTRIBUTING.md)）。
2. **看三蛇打架**：三条不同 AI 策略的蛇在屏幕上自主对抗，直到只剩最后一条。

---

## 🎮 这是什么

基于 **Python + Pygame** 的自动对战贪吃蛇游戏：

| 蛇 | 策略 | 性格 |
|:---:|:---:|:---:|
| 红蛇 | 贪心直冲 | 莽撞，直奔食物 |
| 绿蛇 | BFS 寻路 + 空间评估 | 稳健，会绕障碍保命 |
| 蓝蛇 | 惯性随机游走 | 随性，偶尔捡漏 |

游戏全自动运行，你只需要观赏三条蛇的竞技表演。

---

## 🚀 快速开始

### 环境要求

| 项目 | 要求 |
|:---:|:---:|
| Python | 3.8 及以上（推荐 3.10+） |
| 依赖库 | pygame |
| 显示 | 仅运行可视化游戏时需要图形界面 |

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/HBEU-OSC/hello-open-source.git
cd hello-open-source

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行游戏
python snake_game.py
```

> 💡 提示：Windows 用户如果中文显示为方块，通常是缺少中文字体，详见代码内 `make_font()` 的注释说明。

### 操作

| 按键 | 功能 |
|:---:|:---:|
| `R` | 重新开始一局 |
| `ESC` | 退出游戏 |

---

### 批量模拟与胜率统计

除了可视化游戏，还可以通过命令行自动模拟多局游戏，并统计三种策略的胜率：

```bash
# 模拟 100 局
python snake_game.py --simulate 100

# 设置每局最大步数（默认 10000）
python snake_game.py --simulate 100 --max-steps 5000
```

模拟结果包括：

- **Red / Green / Blue**：各策略的获胜局数和胜率
- **Draws**：平局数量和比例
- **Timeouts**：达到最大步数的局数和比例

胜率以模拟总局数为分母，因此胜率总和不一定为 100%。
批量模拟不需要打开图形游戏窗口。

---

## 🤝 如何参与（新手必读）

**这是本仓库最重要的部分。** 如果你是第一次参与开源，请先完整阅读 [CONTRIBUTING.md](CONTRIBUTING.md)（保姆级教程，包含每一步命令）。

快速流程：

```text
1. Fork 本仓库
2. Clone 到你本地
3. 新建一个分支
4. 做出你的修改
5. 提交并推送
6. 发起 Pull Request
```

只要跑通这个流程，你就完成了人生中第一次开源贡献 🎉

---

## 🎯 认领任务

**想参与开发？** 所有任务都挂在 [Issues](https://github.com/HBEU-OSC/hello-open-source/issues) 里，认领方式：在对应 Issue 下留言即可。

- 新手优先认领带 **`good first issue`** 标签的任务。
- 有新的想法？直接开一个 Issue 提出来。

---

## 📁 目录结构

```text
hello-open-source/
├── README.md               # 项目介绍 + 参与入口
├── CONTRIBUTING.md         # 协作规范（新人必读）
├── LICENSE                 # MIT 开源协议
├── requirements.txt        # 依赖清单
├── snake_game.py           # 游戏主程序及批量模拟
└── tests/
    └── test_simulation.py  # 批量模拟单元测试
```

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE)，可自由使用、修改和分发。
