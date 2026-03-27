# Binary Ninja 插件与资源合集

本仓库汇总与 **Binary Ninja** 相关的用户插件、主题等资源；各子目录可**单独复制**到对应 Binary Ninja 用户目录使用，彼此无强制依赖。

---

## 目录一览

| 目录 | 类型 | 简要说明 |
|------|------|----------|
| [bn-mcp-server](bn-mcp-server/) | Python 插件 | 在 BN **GUI 进程**内提供 **MCP（HTTP）** 服务，供 Cursor 等客户端调用逆向分析工具（函数/HLIL/xref/补丁等）。需安装 `requirements.txt` 依赖。 |
| [bn-hex-comment-fix](bn-hex-comment-fix/) | Python 插件 | 修复反汇编/IL 注释中 **`0x` 十六进制** 导致的文字**重叠、错位**（含中文场景）；含 Render Layer 与可选批量修复。 |
| [bn-theme](bn-theme/) | 主题文件 | **IDA Classic Light** 风格浅色主题（`.bntheme`），放入用户 `themes` 目录后在设置中选主题即可。 |

---

## 各子项目文档入口

| 子项目 | 用户说明 | 其他文档 |
|--------|----------|----------|
| `bn-mcp-server` | [README.md](bn-mcp-server/README.md) | [doc/用户指南.md](bn-mcp-server/doc/用户指南.md)、[doc/README.md](bn-mcp-server/doc/README.md)；内部规格见 [spec/](bn-mcp-server/spec/) |
| `bn-hex-comment-fix` | [README.md](bn-hex-comment-fix/README.md) | [doc/0x注释重叠问题与插件原理教程.md](bn-hex-comment-fix/doc/0x注释重叠问题与插件原理教程.md) |
| `bn-theme` | [README.md](bn-theme/README.md) | [doc/README.md](bn-theme/doc/README.md) |

---

## 安装位置速查（Binary Ninja）

以下为常见用户数据路径，**以你本机 Binary Ninja 实际设置为准**。

| 内容 | 典型路径（Windows） |
|------|----------------------|
| 用户插件 | `%APPDATA%\Binary Ninja\plugins\` |
| 用户主题 | `%APPDATA%\Binary Ninja\themes\` |

macOS / Linux 路径见各子项目 README。

---

## 许可

各子项目若在自身目录内单独声明许可（如 MIT），以该声明为准；未声明时请查看对应源文件或作者说明。
