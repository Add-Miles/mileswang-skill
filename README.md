# mileswang-skill

`mileswang-skill` 是 Miles Wang 的可安装 Codex 工作流合集：对外只有一个品牌和安装入口，内部按任务拆成独立 Skill，并允许以后持续增加真实、可验证的新能力。

当前稳定版本：[`v0.4.0`](https://github.com/Add-Miles/mileswang-skill/releases/tag/v0.4.0)。

它不是把第三方 Skill 改名后重新发布，也不是把 Grok、ChatGPT 或其他模型“封装进一个提示词”。v0.3.0 在既有路由、项目执行与内容创作底盘上，新增已真实验收的 V10 语义视频剪辑能力；X 方法论仍是候选，不冒充已发布能力。

## v0.4.0 包含什么

| Skill | 何时使用 | 产出 |
| --- | --- | --- |
| `mileswang` | 用户只有模糊目标、不确定该用哪个 Skill，或希望调用已安装的第三方 Skill | 依据当前会话 active catalog，路由到精确内部或外部 executor |
| `miles-project` | 开发、迁移、恢复、发布、部署或其他需要真实执行闭环的项目 | 唯一需求合同、版本权威判断、执行与验证路径 |
| `miles-content` | 选题、口播稿、短视频文案、文章等内容需要诊断或改写 | 真实场景与冲突、删减后的成稿、事实与证据边界 |
| `miles-ai-video` | 策划、改编或审查 AI 产品演示与短视频 | 30-90 秒结构、镜头清单、屏幕证据、字幕/口播点和剪辑检查 |
| `miles-x-methodology`（候选） | 分析已提供或真实获取的 X 帖子材料 | 固定五问、证据标签、第一性原理、可迁移行动、未核验主张与最小验证动作；当前等待真实新会话与 Miles 内容验收 |
| `miles-video-editing` | 把一条真实口播视频做成 V10 风格语义剪辑 | 可迁移工作区、语义分镜、信息卡、空间避让、HyperFrames 检查与成片验收；已通过两条真人视频、用户确认和隔离安装验收 |
| `miles-update` | 用户明确说“更新 mileswang”或检查 Miles 更新 | 只检查或安装官方最新稳定版；保护其他插件，失败回退，要求新会话生效 |

## 两类能力，一个入口

`mileswang-skill` 的长期能力分成两类，不能混为一谈：

- **Miles 自有能力**：由 Miles 定义、验证和发布。已发布能力包括 `miles-project`、`miles-content`、`miles-ai-video`、`miles-video-editing` 和 `miles-update`；`miles-x-methodology` 仍是候选，完成真实内容验收前不算稳定发布。
- **外部专业能力**：由其他作者独立安装和维护。`mileswang` 只在该 Skill 出现在当前会话 active catalog 且确实适合任务时，保留其完整规范名并委托执行。

路线图中的候选能力不是已发布 Skill。候选项只有获得真实输入、认可结果或 Golden Sample、独立触发边界、合法来源和真实路径验收后，才会在单独迭代中成为新的 `miles-*` 模块。

## 系统怎样衔接任务

统一入口有三种行为：

1. 第一次使用时，说明可以提交什么、系统怎样选一个执行者、可能得到什么结果，然后接住用户当前的真实任务。
2. 任务开始前，只选择一个当前执行者；不会让用户先学习完整目录。
3. 一个 Skill 完成后，根据它的具体结果和用户最新反馈决定至多一个下一步；任务已经完成就停止，不预设固定 Skill 流水线。

能力状态由 `capability-map.json` 明确区分为 `released-owned`、`candidate-owned`、`external-runtime` 和 `future-candidate`。外部能力是否可用仍只由当前会话 active catalog 决定，能力地图不能替代运行时判断。

仓库还提供一份可移植的 [`templates/AGENTS.md`](templates/AGENTS.md)。它是可选的项目规则模板，安装插件不会自动覆盖你现有的全局或项目级 `AGENTS.md`。

## 安装

使用固定 tag 安装：

```bash
codex plugin marketplace add Add-Miles/mileswang-skill --ref v0.4.0
codex plugin add mileswang-skill@mileswang-skill
```

安装后重启 ChatGPT 桌面端或重新打开 Codex 会话，使插件目录刷新。

安装只证明插件已进入本地目录，不证明它已经替你完成任何项目或提升任何内容表现。实际效果必须用真实输入和真实产出验证。

### 更新已安装的 Skill

`v0.3.0` 及更早版本不包含更新器，必须先手动执行上面的 `v0.4.0`
安装命令完成一次迁移。从 `v0.4.0` 开始，后续更新才可以直接说：

安装包含 `miles-update` 的稳定版本后，直接说：

```text
更新 mileswang
```

系统只检查并更新官方 `Add-Miles/mileswang-skill` 到 GitHub 最新正式
Release，不更新其他插件，也不追踪未经发布的 `main`。更新失败时尝试恢复
原稳定版本；成功后必须新开对话才能加载新目录。

这不是后台实时更新：不会创建定时任务、启动项或静默网络请求。更新检查
使用 GitHub 的公开 Release 和 raw-content 端点，不需要 Miles API、API
Key、账号或私有服务。

## 隐私边界

公开允许的个人品牌只有 `Miles Wang`、`Miles`、`Add-Miles`、`mileswang`
和 `mileswang-skill`。私人邮箱、电话、地址、机器路径、账号标识、聊天、
凭据及不必要的脸部、声音和媒体元数据不得进入公开输出、日志、错误、
Agent 交接或发布包。

所有内置 Skill 都必须在输出前执行隐私 Gate；公开文件、发布包和可发布的
heads/tags 历史也由 CI 扫描。历史重写无法删除他人的克隆或宿主缓存，这些需要
仓库托管方另行清理，不能把强推冒充成完整擦除。

### 剪视频的本地依赖

`miles-video-editing` 不使用 Miles 的 API、API Key、账号或私有服务，也
不要求额外安装 `media-use`、`hyperframes` 或 `hyperframes-cli` Skill。

第一次剪视频前，本机需要 Python 3.10+、Node.js 22+、npm/npx、FFmpeg
和 ffprobe。Skill 会先离线检查这些条件；经用户明确同意后，只在当前
视频项目内安装固定版本的公开 `hyperframes@0.7.81`，并按需下载浏览器
和本地 Whisper 模型。转写、检查与渲染都在用户自己的机器上完成，不
需要任何 API Key。

首次安装 npm 包、浏览器、字体或模型会访问公开依赖源，可能产生网络
流量和磁盘占用；这不等于调用 Miles API。marketplace 清单中的安装期
策略字段也不代表存在 Miles 登录或认证服务，本仓库没有认证端点。

## 怎么使用

直接描述任务即可，例如：

```text
我有三个产品想法，但两周内只能完成一个。请先帮我收束并给出可验证的本轮交付。
```

```text
这是一段短视频逐字稿。保留事实，找出真实场景和冲突，删掉自我感动与空话。
```

```text
这是一个 X 帖子的正文和截图。区分来源、事实摘要、AI 推断和未核验主张，分析它的第一性原理、方法论，以及我能做的最小验证动作。
```

```text
用 mileswang 剪这条口播视频。先做依赖预检和语义分镜，最终预览未经我确认不要渲染。
```

```text
我要发布这个项目。先确认唯一权威版本、回退位置和真实验收路径，再执行。
```

```text
更新 mileswang。只更新这个插件，成功后告诉我新版本号。
```

如果任务明确属于某个模块，也可以直接点名对应叶子。`miles-video-editing` 拥有 Miles 的 V10 方法，并默认使用项目内固定版本的公开本地工具链完成转写和渲染；只有用户明确指定其他 active Skill 时才委托外部执行，并保留其原名。

## 路由其他作者的 Skill

`mileswang` 可以把任务交给当前会话已经公布的第三方 Skill，但不会把第三方内容收进 Miles 仓库。

路由只认宿主提供的 active Skill catalog：

- `internal`：使用 `miles-project`、`miles-content`、`miles-ai-video`、`miles-video-editing`，或候选 `miles-x-methodology`、`miles-update`；
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
│       ├── miles-content/
│       ├── miles-ai-video/
│       ├── miles-x-methodology/
│       ├── miles-video-editing/
│       └── miles-update/
├── templates/AGENTS.md
├── tools/
│   ├── new_skill.py
│   ├── validate.py
│   ├── check_routing_contract.py
│   ├── check_update_contract.py
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
python3 tools/check_system_contract.py
python3 tools/check_x_methodology_contract.py
python3 tools/check_video_v10_contract.py
python3 tools/check_update_contract.py
python3 tools/check_privacy_contract.py
```

`check_system_contract.py` 还会拒绝以下伪能力：候选能力提前绑定 executor、外部能力被写成静态可用、已发布自有能力没有真实目录，以及真实 Miles 叶子没有登记为已发布能力。

`miles-x-methodology` 只负责分析真实取得的材料，不内置 X 抓取、账号能力、自动收藏、飞书写入或作者数据库。只有 URL 时，入口应把内容获取交给当前会话真实可用的外部浏览器或研究 Skill，并保留外部身份。

### 个人 Markdown 升级 Gate

个人原文不进入公开仓库。`source-manifest.json` 只登记公开安全的来源 ID、确认状态、基线哈希和 `local-only` 分发边界。检查当前文件是否漂移：

```bash
python3 tools/check_source_drift.py \
  --source 'GS-01-V1=/path/to/current-golden-sample.md'
```

需要比较稳定文件和候选文件时：

```bash
python3 tools/check_source_drift.py \
  --compare '/path/to/stable.md=/path/to/candidate.md'
```

命令只向控制台输出哈希状态或统一 diff，不修改稳定 Skill。检测到变化时返回非零状态；只有同一 Golden Sample 回归不退步并获得 Miles 确认后，才能更新规则、哈希和能力状态。

## 维护与发布

`VERSION` 是唯一版本输入。每次发布必须同步插件 manifest 和本页的稳定版本、安装 ref；CI 会拒绝不一致。完整本地 Gate：

```bash
python3 tools/validate.py
python3 tools/check_routing_contract.py
python3 tools/check_system_contract.py
python3 tools/check_x_methodology_contract.py
python3 tools/check_video_v10_contract.py
python3 tools/check_update_contract.py
python3 tools/check_privacy_contract.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/build_release.py --output-dir dist
python3 -m zipfile -t dist/mileswang-skill-v0.4.0.zip
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
