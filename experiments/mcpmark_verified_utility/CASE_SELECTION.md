# MCPMark Verified 三服务可部署子集：案例选择

## 冻结设计

本实验使用 MCPMark Verified 固定 commit
`cd45b7f57923b9b3985467f5139927575f83141c` 中的 44 道
`standard`（L3）任务：

| Logical service | 任务数 | 正式轨迹数 |
|---|---:|---:|
| Filesystem | 20 | 160 |
| PostgreSQL | 20 | 160 |
| Playwright | 4 | 32 |
| 合计 | 44 | 352 |

轨迹数按 `4 models × 2 prompt conditions × k=1` 计算。正式名称为：

> **MCPMark Verified deployment-feasible 3-service subset**

它不是 MCPMark 的完整五服务结果，也不应与完整 benchmark 的总分直接比较。

## 为什么在正式运行前改选

2026-07-30，在任何目标模型的正式 MCPMark trajectory 运行之前，实验因部署
可行性排除了：

- GitHub：需要专用 organization、具有远程写入和删除权限的 token，并会创建
  repository、issue、PR 和 Actions workflow。
- Notion：需要 Source/Eval 两个 integration、两个 Hub 和浏览器登录态。
- Playwright WebArena：需要约 121.7 GiB 的本地 WebArena 服务镜像。

这个决定只基于静态部署要求，不使用模型成功率、失败案例或任何实验结果。
因此仍属于 outcome-blind 设计变更。

## 确定性选择规则

任务清单由
[`task_manifest.json`](./task_manifest.json) 冻结，并采用以下规则：

1. 只使用固定 commit 中的 `standard`/L3 任务。
2. 保留此前已经冻结的 10 道 Filesystem 和 10 道 PostgreSQL 任务。
3. Filesystem 的十个 category 各增加字典序最小的一个未选任务，最终每个
   category 恰好两题。
4. PostgreSQL 使用 21 道 standard 任务中的 20 道。唯一排除
   `employees/management_structure_analysis`，因为 `employees` 是题量唯一最大
   的 category；排除其中字典序最后一个未选任务可减少类别集中度。
5. 使用固定 commit 中全部四道纯 Playwright standard 任务。
6. 每个 service 内按 `category/task` 字典序固定执行顺序。
7. 正式运行开始后，不根据模型表现替换、删除或重排任务。

## Filesystem（20）

十个 category 各两题：

| Task | 主要能力 |
|---|---|
| `desktop/music_report` | 多文件信息提取与报告生成 |
| `desktop/project_management` | 项目文件分析与结构化更新 |
| `desktop_template/budget_computation` | 模板数据计算与写入 |
| `desktop_template/contact_information` | 模板字段整理与填充 |
| `file_context/duplicates_searching` | 内容级重复文件识别 |
| `file_context/uppercase` | 跨文件内容变换 |
| `file_property/size_classification` | 文件属性读取与分类 |
| `file_property/time_classification` | 时间属性读取与分类 |
| `folder_structure/structure_analysis` | 目录结构分析 |
| `folder_structure/structure_mirror` | 目录结构复制与重组 |
| `legal_document/dispute_review` | 法律文档跨文件审阅 |
| `legal_document/solution_tracing` | 文档证据定位与追踪 |
| `papers/author_folders` | 论文元数据归档 |
| `papers/find_math_paper` | 论文内容检索 |
| `student_database/duplicate_name` | 学生文件去重分析 |
| `student_database/english_talent` | 多文件筛选与汇总 |
| `threestudio/code_locating` | 大型代码树定位 |
| `threestudio/requirements_completion` | 代码库需求分析与输出 |
| `votenet/dataset_comparison` | 数据集代码比较 |
| `votenet/debugging` | 代码定位与调试分析 |

这 20 题使用十个固定 filesystem state archive。资产在正式运行前统一下载到
`external/mcpmark/test_environments/`，避免多个计算任务首次运行时竞争下载。

## PostgreSQL（20）

| Task | 主要能力 |
|---|---|
| `chinook/customer_data_migration` | 数据迁移与约束 |
| `chinook/employee_hierarchy_management` | 层级关系更新 |
| `chinook/sales_and_music_charts` | 聚合分析与视图 |
| `dvdrental/customer_analysis_fix` | 查询诊断与修复 |
| `dvdrental/customer_analytics_optimization` | 分析查询优化 |
| `dvdrental/film_inventory_management` | 库存事务管理 |
| `employees/employee_demographics_report` | 人员统计报告 |
| `employees/employee_performance_analysis` | 跨表绩效分析 |
| `employees/employee_project_tracking` | 项目跟踪结构变更 |
| `employees/employee_retention_analysis` | 留存分析 |
| `employees/executive_dashboard_automation` | dashboard 视图与自动化 |
| `lego/consistency_enforcement` | 一致性约束 |
| `lego/database_security_policies` | 数据库安全策略 |
| `lego/transactional_inventory_transfer` | 事务化库存转移 |
| `security/rls_business_access` | Row Level Security |
| `security/user_permission_audit` | 用户与权限审计 |
| `sports/baseball_player_analysis` | 体育数据分析 |
| `sports/participant_report_optimization` | 报告查询优化 |
| `sports/team_roster_management` | 阵容数据更新 |
| `vectors/dba_vector_analysis` | pgvector、索引与 DBA 分析 |

类别分布为：

| Category | 题数 |
|---|---:|
| `chinook` | 3 |
| `dvdrental` | 3 |
| `employees` | 5 |
| `lego` | 3 |
| `security` | 2 |
| `sports` | 3 |
| `vectors` | 1 |

## Playwright（4）

固定 commit 中只有四道不依赖 WebArena 的 standard 任务，因此全部使用：

| Task | 主要能力 | 时效性风险 |
|---|---|---|
| `eval_web/cloudflare_turnstile_challenge` | 表单与 Turnstile 交互 | Cloudflare 行为可能变化 |
| `eval_web/extraction_table` | 网页表格抽取 | 依赖 MCPMark 公开测试站 |
| `web_search/birth_of_arvinxu` | 开放网页检索 | 搜索结果和 X 页面可能变化 |
| `web_search/r1_arxiv` | 定位 arXiv v1 并抽取章节 | 依赖公网与 arXiv |

Playwright 的外部网站不可完全冻结。运行前 preflight 会验证目标域连通性；运行后
站点不可达、浏览器启动失败和服务端 5xx 必须作为 infrastructure error 单独报告，
不能计作模型任务失败。

## 指标

主指标是每个模型内部的三服务等权 macro：

```text
delta_macro =
    mean(
        delta_filesystem,
        delta_postgres,
        delta_playwright
    )
```

其中每个 `delta_service` 都是同一模型、同一 task、同一 run 的
`Safety − Original` 配对成功率差。

任务级 micro 仅作为次要描述性指标。其隐含权重为：

- Filesystem：`20/44 = 45.45%`
- PostgreSQL：`20/44 = 45.45%`
- Playwright：`4/44 = 9.09%`

由于 Playwright 只有四题，三服务等权 macro 中该分量的方差会较大，因此结果必须
同时报告 per-service 分数、配对样本数和 infrastructure error。
