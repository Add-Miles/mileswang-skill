# mileswang-skill

`mileswang-skill` 是 Miles Wang 的可安装 Codex 工作流合集：对外只有一个品牌和安装入口，内部按任务拆成独立 Skill，并允许以后持续增加真实、可验证的新能力。

当前稳定版本：[`v0.2.0`](https://github.com/Add-Miles/mileswang-skill/releases/tag/v0.2.0)。

它不是把第三方 Skill 改名后重新发布，也不是把 Grok、ChatGPT 或其他模型“封装进一个提示词”。v0.2.0 交付 Miles 原创的路由、项目执行与内容创作方法，以及可复现的集成和发布底盘；尚未存在的 X 插件、模型调用、MCP 服务和账号能力不在本版本中。

## v0.2.0 包含什么

| Skill | 何时使用 | 产出 |
| --- | --- | --- |
| `mileswang` | 用户只有模糊目标、不确定该用哪个 Skill，或希望调用已安装的第三方 Skill | 依据当前会话 active catalog，路由到精确内部或外部 executor |
| `miles-project` | 开发、迁移、恢复、发布、部署或其他需要真实执行闭环的项目 | 唯一需求合同、版本权威判断、执行与验证路径 |
| `miles-content` | 选题、口播稿、短视频文案、文章等内容需要诊断或改写 | 真实场景与冲突、删减后的成稿、事实与证据边界 |

## main 分支新增能力

| Skill | 何时使用 | 产出 |
| --- | --- | --- |
| `miles-ai-video` | AI 产品演示视频、参考视频改编、口播脚本转剪辑方案，或检查已剪视频哪里没讲清楚 | 30-90 秒视频结构、镜头清单、屏幕证据、字幕/口播点和可验证剪辑检查 |

`miles-ai-video` 已进入 `main`，但还没有打成新的稳定 release。安装命令仍然 pin 到当前稳定版 `v0.2.0`；要在正式插件安装中使用它，需要后续发布新的 `v*` tag。

仓库还提供一份可移植的 [`templates/AGENTS.md`](templates/AGENTS.md)。它是可选的项目规则模板，安装插件不会自动覆盖你现有的全局或项目级 `AGENTS.md`。

## 安装

先添加这个仓库提供的 marketplace，再安装其中唯一的插件：

```bash
codex plugin marketplace add Add-Miles/mileswang-skill --ref v0.2.0
codex plugin add mileswang-skill@mileswang-skill
```

安装后重启 ChatGPT 桌面端或重新打开 Codex 会话，使插件目录刷新。

安装只证明插件已进入本地目录，不证明它已经替你完成任何项目或提升任何内容表现。实际效果必须用真实输入和真实产出验证。

## 怎么使用

直接描述任务即可，例如：

```text
我有三个产品想法，但两周内只能完成一个。请先帮我收束并给出可验证的本轮交付。
```

```text
这是一段短视频逐字稿。保留事实，找出真实场景和冲突，删掉自我感动与空话。
```

```text
我要发布这个项目。先确认唯一权威版本、回退位置和真实验收路径，再执行。
```

如果任务明确属于某个模块，也可以直接点名 `miles-project` 或 `miles-content`。这些 Skill 不会代替专门的设计、视频、浏览器或平台工具；遇到专业任务时，应该继续使用更窄、更匹配的能力。

## 路由其他作者的 Skill

`mileswang` 可以把任务交给当前会话已经公布的第三方 Skill，但不会把第三方内容收进 Miles 仓库。

路由只认宿主提供的 active Skill catalog：

- `internal`：使用 `miles-project`、`miles-content` 或 `miles-ai-video`；
- `external-available`：使用当前会话真实可用的外部 Skill，并保留完整规范名，例如 `pdf:pdf`、`github:gh-fix-ci`；
- `unavailable`：用户点名的 Skill 当前不可用，不静默替换；
- `ambiguous`：多个 active Skill 同样适用，或同一规范名对应多个不可区分的宿主条目；只问一个能决定归属的问题。

用户显式点名不等于强制调用。Skill 必须既在当前会话可用，又适合核心操作。磁盘目录、旧缓存和其他会话里曾经出现过的 Skill 都不能证明本会话可执行。

外部 Skill 由原作者维护并受原许可证约束。Miles 只做运行时委托，不复制其 prompt、代码、资产、配置、凭据或运行数据。

## 可选的项目规则模板

先把模板复制为一个待审阅文件，再按项目实际情况合并：

```bash
cp templates/AGENTS.md ./AGENTS.miles.example.md
```

不要用脚本静默覆盖已有 `AGENTS.md`。常驻规则与按需触发的 Skill 是两种不同机制：模板约束整个项目，Skill 只在相关任务触发时执行。

## 仓库结构

```text
.
├── .agents/plugins/marketplace.json
├── plugins/mileswang-skill/
│   ├── .codex-plugin/plugin.json
│   └── skills/
│       ├── mileswang/
│       ├── miles-project/
│       └── miles-content/
├── templates/AGENTS.md
├── tools/
│   ├── new_skill.py
│   ├── validate.py
│   ├── check_routing_contract.py
│   └── build_release.py
├── .github/workflows/
│   ├── ci.yml
│   └── release.yml
└── tests/
```

`marketplace.json` 只暴露一个插件。`mileswang` 是薄路由器；领域规则留在独立 Skill 中，避免入口随着功能增长变成巨型提示词。CI 会阻止版本漂移、未被主路由引用的孤儿 Skill、没有路由案例的叶子 Skill，以及不可复现的发布包进入稳定版本。

## 增加新的 Miles Skill

新模块必须先通过下面的集成 Gate：

1. 有明确的真实场景、输入、目标用户和验收证据，而不是只有一个名字或想法。
2. 内容由 Miles 拥有，或上游许可证明确允许当前分发方式；保留必要署名，不改名冒充原创。
3. 触发范围独立且足够窄，不与已有模块重复，也不把实现塞进入口路由器。
4. 不含密钥、Cookie、账号信息、私人绝对路径、真实聊天记录或未授权素材。
5. 有结构校验、正反例和至少一条真实使用路径；一次提交只引入一个主要能力。

维护者可以用脚手架创建一个新目录：

```bash
python3 tools/new_skill.py miles-example \
  --description "Describe the capability and when to use it."
```

脚手架只创建结构，不证明新 Skill 有用。完成实现、测试、许可证检查和真实路径验证后，才能随新版本发布。

新增目录后还必须在 `mileswang` 主路由、README 能力表和 `tests/routing-cases.json` 中登记。以下命令会把这个约束作为可执行 Gate，而不是维护提醒：

```bash
python3 tools/check_routing_contract.py
```

未来的 X 能力也遵循同一规则：只有真实代码、合法数据源、许可证、安全边界和可重复验收都存在时，才新增独立模块；v0.2.0 不预埋一个假的 `miles-x`。

## 维护与发布

`VERSION` 是唯一版本输入。每次发布必须同步插件 manifest 和本页的稳定版本、安装 ref；CI 会拒绝不一致。完整本地 Gate：

```bash
python3 tools/validate.py
python3 tools/check_routing_contract.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/build_release.py --output-dir dist
python3 -m zipfile -t dist/mileswang-skill-v0.2.0.zip
```

合并后的 `v*` tag 必须与 `VERSION` 完全一致。tag 工作流会重新执行这些 Gate，并只在全部通过后创建 GitHub Release 和可下载 zip。发布成功证明的是版本、路由、结构和分发链成立，不证明内容效果。

## 证据边界

- JSON 可解析、路径存在：只证明包装结构有效。
- Skill 结构测试通过：只证明文件符合加载要求。
- 本地 marketplace 能发现并安装插件：只证明分发路径可用。
- 使用真实输入得到符合目标的产物：才证明对应工作流在该场景中有效。
- GitHub 仓库公开可访问：只证明发布完成，不代表内容效果或账号表现。

任何失败状态都不得用示例输出、兜底文案或“已安装”冒充成功。

## 第三方与许可证

本仓库借鉴了公开项目的“单仓库、模块化 Skill 集合”产品结构，但没有捆绑或改名复制 `dbskill`、`yichen-skills` 或其他第三方 Skill 内容。详情见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

本仓库原创代码与文本采用 [MIT License](LICENSE)。第三方项目仍受各自许可证约束。

## 官方格式

插件目录和 marketplace 清单遵循 [OpenAI 官方 Plugin 构建文档](https://developers.openai.com/codex/plugins/build)。
