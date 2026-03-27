# IDA Classic Light（Binary Ninja 主题）

本仓库提供 **IDA Pro 经典浅色** 风格的 Binary Ninja 配色主题，界面风格为 **Fusion**，适合习惯 IDA 浅色配色、希望在 BN 里保持相近阅读体验的用户。

---

## 包含文件

| 文件 | 说明 |
|------|------|
| `ida-classic-light.bntheme` | 主题定义（JSON），含通用调色板与反汇编/图/特性图等 `theme-colors` |

---

## 安装与启用

1. **复制主题文件**到 Binary Ninja **用户主题目录**，例如：
   - **Windows**：`%APPDATA%\Binary Ninja\themes\`
   - **macOS**：`~/Library/Application Support/Binary Ninja/themes/`
   - **Linux**：`~/.binaryninja/themes/`  

   若 `themes` 文件夹不存在，可自行新建。

2. **重启 Binary Ninja**（部分版本在复制后需重启才能出现在列表中）。

3. 打开 **Settings → Theme**（或 **Edit → Preferences → Theme**，以你的 BN 版本菜单为准），在主题列表中选择 **IDA Classic Light** 并应用。

若你的 Binary Ninja 支持 **从文件导入主题**，也可在主题相关对话框中直接选择本仓库的 `ida-classic-light.bntheme`。

---

## 说明

- 主题为 **浅色** 背景，寄存器、立即数、符号、字符串等颜色尽量贴近常见 IDA 经典浅色观感；具体以 Binary Ninja 渲染与版本为准。
- 修改配色可编辑 `ida-classic-light.bntheme` 中的 `colors`、`palette` 与 `theme-colors`；更细的字段说明可参考 Binary Ninja 官方文档中关于 **主题** 的章节。

---

## 文档目录

- **`doc/`**：预留说明与扩展文档（若将来补充调色对照表、自定义说明等，可放在此处）。索引见 [doc/README.md](doc/README.md)。

---

## 许可

以本仓库单独声明的许可文件为准；若未提供，请在使用与分发前自行确认作者或版权约定。
