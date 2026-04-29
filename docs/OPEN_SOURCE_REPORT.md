# LPS-Bench Open-Source Release Report

生成日期：2026-04-29

远端仓库：`git@github.com:tychenn/LPS-Bench.git`

## 开源范围

本次开源包围绕论文中的 LPS-Bench 可复现资产整理，包含基准数据、模拟工具、评估代码、skill 扩展和必要文档。

| 路径 | 内容 | 开源原因 |
| --- | --- | --- |
| `README.md` | 项目说明、运行命令、数据结构和引用信息 | 让外部用户能够理解并运行 benchmark |
| `LICENSE` | MIT 许可证 | 明确代码和数据的使用许可 |
| `.gitignore` | 本地产物和私有文件排除规则 | 防止提交论文 PDF、运行日志、缓存、私有配置和内部脚本 |
| `agent.py` | LangChain agent runner，支持批量 case、自动评价和 skill capability modes | 复现实验执行和 skill-only/tool-only/hybrid 对比的核心入口 |
| `multi-agent_pipeline.py` | 多 agent case 生成 pipeline | 对应论文中的 benchmark construction pipeline；已改为从环境变量读取 API 配置 |
| `evaluator/` | 9 类风险的 LLM-as-judge 评估器 | 对应论文的 trajectory-level safety evaluation |
| `examples/` | 570 个 base cases + 41 个 skill-augmented cases | 论文贡献的核心 benchmark 数据集 |
| `tools/` | 571 个 mock tool 文件 | 为每个 case 提供沙盒化、无真实副作用的工具环境 |
| `prompt/` | 9 类风险的数据生成 prompt 模板 | 支撑 benchmark 扩展和复现 case synthesis |
| `skill_assets/` | 88 个 case-local `SKILL.md` 文件 | skill-augmented extension 所需的可复用技能文本 |
| `schemas/lps_case_v2.schema.json` | case JSON schema | 约束和校验数据格式 |
| `scripts/` | skill 实验 case list 构建和结果汇总脚本 | 复现 skill 扩展实验分析 |
| `docs/` | case 设计说明、skill shortlist 和本报告 | 解释数据设计、筛选逻辑和开源整理决策 |

## 数据集统计

Base cases：570

| Domain | Cases |
| --- | ---: |
| `webbrowser` | 92 |
| `code` | 90 |
| `fileio` | 85 |
| `multi_media` | 78 |
| `social_media` | 77 |
| `OS_operation` | 76 |
| `office` | 72 |

| Risk | Base cases |
| --- | ---: |
| `FA` | 68 |
| `HS` | 68 |
| `PI` | 67 |
| `IP` | 67 |
| `MT` | 66 |
| `EB` | 65 |
| `OC` | 62 |
| `TS` | 55 |
| `RC` | 52 |

Skill-augmented cases：41

| Risk | Skill cases |
| --- | ---: |
| `FA` | 10 |
| `OC` | 10 |
| `PI` | 11 |
| `TS` | 10 |

## 不开源或不提交的内容

| 路径 | 原因 |
| --- | --- |
| `neurips_latex.pdf` | 论文 PDF，不是代码或数据集本体；可能涉及匿名投稿和版本管理，不放入代码仓库 |
| `runs/` | 原始运行日志、Slurm 输出和临时实验目录；不是最小复现资产，且可能包含环境细节或模型输出噪声 |
| `records/` | 本地执行轨迹输出目录；由用户运行后生成，不应作为源数据提交 |
| `figure/` | 论文绘图和派生可视化，不是 benchmark 运行所需文件；README 已去掉对这些本地图片的依赖 |
| `OSWorld/` | 外部项目本地副本，体积大且有独立许可和维护边界；当前 LPS-Bench 代码不依赖提交该目录 |
| `.vscode/`, `.claude/`, `CLAUDE.md` | 本地 IDE/agent 配置和开发说明，和公开复现无关 |
| `__pycache__/`, `scripts/__pycache__/`, `tools/__pycache__/` | Python 缓存产物 |
| `agent_batch.py`, `agent_original.py`, `mcp_agent.py`, `evaluate_only.py` | 内部/历史 runner，包含本地路径或凭据风险；公开入口统一为 `agent.py` |
| `generate_case.py`, `generate_hs_case.py`, `generate_test_case_comments.py` | 旧版生成脚本，已由 `multi-agent_pipeline.py` 和 `prompt/` 覆盖 |
| `prompt_backup/`, `tools_unused_backup/` | 备份和废弃素材，不属于最终 benchmark |

## 清理和安全处理

- 已从开源的 `multi-agent_pipeline.py` 中移除硬编码 API key，改为读取 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`。
- 已修改 `scripts/run_local_skill_case_modes_slurm.sh` 和 `scripts/run_local_skill_model_slurm.sh`，不再依赖私有 `agent_batch.py` 或打印 API key。
- 已扩展 `.gitignore`，排除论文 PDF、运行日志、缓存、私有配置和内部脚本。
- 已执行敏感 key 形态扫描；开源范围内未发现 `sk-...`、GitHub token、AWS key 或私钥块。

## 验证结果

- JSON 解析检查：`examples/` 下所有 case JSON 均可解析。
- 工具引用检查：所有 case 中 `MCP.file` 引用的 `tools/` 文件均存在。
- 语法检查：`agent.py`、`multi-agent_pipeline.py` 和 `scripts/` 下的 Python 脚本通过 `py_compile`。
- 运行环境检查：当前 shell 缺少 `langchain`，因此 `python agent.py --help` 无法执行；按 README 安装依赖后可运行。

## 当前仓库文件结构

当前公开仓库应包含以下顶层文件和目录：

```text
.
├── .gitignore
├── LICENSE
├── README.md
├── agent.py
├── multi-agent_pipeline.py
├── docs/
├── evaluator/
├── examples/
├── prompt/
├── schemas/
├── scripts/
├── skill_assets/
└── tools/
```
