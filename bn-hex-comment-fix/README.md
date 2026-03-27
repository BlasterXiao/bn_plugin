# Hex Comment Fix（Binary Ninja 插件）

修复 **反汇编 / IL 视图** 中行尾注释里出现 `0x` 十六进制写法时，**后半段文字与前面叠在一起**或 **中文注释更容易错位** 的显示问题。

---

## 适用场景

- 在注释里写地址或常量，例如 `0xdeadbeef`、`0x50`；
- 注释里混用 **中文** 与十六进制，更容易触发错位；
- 你希望 **不改动 Binary Ninja 本体**，只通过用户插件改善显示。

---

## 安装

1. 将本仓库中的 **`hex_comment_fix.py`** 复制到 Binary Ninja **用户插件目录**，例如：
   - **Windows**：`%APPDATA%\Binary Ninja\plugins\`
   - **macOS**：`~/Library/Application Support/Binary Ninja/plugins/`
   - **Linux**：`~/.binaryninja/plugins/`  
   也可单独建子文件夹（如 `hex-comment-fix/hex_comment_fix.py`），只要 BN 能加载到该 `.py` 即可。

2. **重启 Binary Ninja**（或按你的环境重载插件）。

3. 无需额外 `pip` 依赖（仅用 Python 标准库与 Binary Ninja 自带 API）。

---

## 使用方法

### 1. 渲染层（默认已生效）

插件加载后，会注册名为 **「Hex Comment Fix」** 的 **Render Layer**（显示层），用于在绘制前修正 token 类型与宽度。

- 在菜单 **View → Render Layers** 中确认 **Hex Comment Fix** 已勾选（一般默认开启）。

### 2. 每份二进制执行一次「自动修复」（推荐）

打开目标二进制后，执行菜单：

**Plugins → Hex Comment Fix → Enable Auto-Fix**

作用包括：

- **批量处理**当前数据库里已有注释（在 `0` 与 `x` 之间插入不可见的零宽字符，打断 BN 对 `0x` 的十六进制 token 识别）；
- **注册**后续新加、修改注释时的自动处理。

### 3. 撤销

**Plugins → Hex Comment Fix → Undo All Fixes** — 从注释中移除上述插入的零宽字符（恢复存储内容）。

### 4. 调试（可选）

**Plugins → Hex Comment Fix → Debug: Dump Comment Tokens** — 将含注释行的 token 信息输出到 Binary Ninja **日志**，便于排查问题（仅处理第一个函数作为示例）。

---

## 原理（一句话）

Binary Ninja 可能把注释里的 `0x…` 当成地址/整数类 token 绘制，且注释 token 的 `width` 对 **中日韩等宽字符** 计数不准；本插件用 **零宽字符（ZWSP）** 打断 `0x` 模式，并用 **RenderLayer** 在显示层把注释内的 token 类型与宽度修正为更安全的表现。

更完整的图文教程与实现步骤见 [doc/0x注释重叠问题与插件原理教程.md](doc/0x注释重叠问题与插件原理教程.md)；文档索引见 [doc/README.md](doc/README.md)。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `hex_comment_fix.py` | 插件主程序（复制到 BN 用户插件目录） |
| `doc/` | 原理与从零开发教程（给想深入理解或二开的读者） |

---

## 许可

以 `hex_comment_fix.py` 或仓库内单独提供的许可文件为准。
