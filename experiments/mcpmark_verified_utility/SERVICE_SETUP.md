# 三服务环境说明

本实验只运行 Filesystem、PostgreSQL 和纯 Playwright 三类 MCPMark Verified
任务。不需要 GitHub token、Notion integration、Notion Cookie 或 WebArena。

## 一次性准备

在仓库根目录执行：

```bash
bash experiments/mcpmark_verified_utility/setup_environment.sh
bash experiments/mcpmark_verified_utility/prepare_service_assets.sh
```

第一条命令准备：

- MCPMark Python 虚拟环境；
- PostgreSQL 17 客户端；
- 固定版本的 Filesystem、PostgreSQL 和 Playwright MCP runtime；
- Python Playwright Chromium；
- Node Playwright MCP 使用的 Chromium。

第二条命令准备：

- 十个 Filesystem category archive 及其解压目录；
- 五个 PostgreSQL 初始数据库 backup；
- `pgvector/pgvector:0.8.0-pg17-bookworm` 容器 archive。

Filesystem 和 PostgreSQL 下载资产会记录本地 SHA-256。后续
`--check-only` 会验证 archive、解压树和 PostgreSQL backup，避免损坏资产进入
正式实验。

旧版本实验已经下载的 GitHub state 或 GitHub MCP image 可以留在磁盘上。新脚本
不会读取、下载或删除它们，也不会要求它们存在。

## 完整检查

下载完成后执行：

```bash
bash experiments/mcpmark_verified_utility/setup_environment.sh --check-only
bash experiments/mcpmark_verified_utility/prepare_service_assets.sh --check-only
experiments/mcpmark_verified_utility/.venv/bin/python \
  experiments/mcpmark_verified_utility/run_experiment.py validate
```

三条命令都必须成功，才能开始正式运行。

## Filesystem

正式 runner 会强制使用：

```text
external/mcpmark/test_environments/
```

该目录下必须存在以下十个非空目录：

```text
desktop
desktop_template
file_context
file_property
folder_structure
legal_document
papers
student_database
threestudio
votenet
```

每道题开始前，上游 state manager 会把对应 category 复制到 PID 唯一的工作目录；
模型只修改工作副本，结束后删除副本。原始 state 保持不变。

Filesystem 不需要账号或 secret。正式 gpu3 直接调度会保证同一 service 全局
互斥，避免上游初始化阶段对共享 state root 的并发探测发生竞争。

## PostgreSQL

直接 worker 会为每个 PostgreSQL 单元：

1. 使用该 `EXP` 专属的 gpu3 本地 Podman graphroot，而不是 NFS home 中的默认
   rootless store；
2. 从共享 archive 加载固定 pgvector PG17 镜像；
3. 在 gpu3 缺少 subuid/subgid 的情况下，将宿主用户映射为容器内 PostgreSQL
   用户 `999:999`；
4. 生成随机数据库密码；
5. 启动一个带 owner label 的专用容器；
6. 仅把随机端口绑定到 `127.0.0.1`；
7. 设置本 worker 的连接环境变量；
8. 在同一容器中依次运行 Original/Safety；
9. 校验 owner label 后删除容器和 volume。

密码只存在于 worker 环境和权限为 `600` 的临时文件中；临时文件在容器启动后立即
删除。用户不需要申请 PostgreSQL API，也不需要手工设置正式实验密码。

入口脚本只为实验子进程设置 `CONTAINERS_STORAGE_CONF` 和 Podman runtime。它不会
修改 `~/.config/containers/storage.conf`，也不会清理或复用旧失败轮的默认 NFS
container store。

如果绕过正式 worker，直接运行 `run_experiment.py run --services postgres`，
则调用者必须自己启动兼容 PostgreSQL 17/pgvector 的数据库，并设置：

```bash
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=postgres
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD='local-test-password'
```

正式实验使用 `run_gpu3_experiment.sh` 自动管理专用数据库，不要复用人工维护的
数据库。

## Playwright

四道 Playwright 题需要访问：

- `eval-web.mcpmark.ai`
- `arxiv.org`
- X 页面或可索引它的公开搜索结果

不需要登录账号。浏览器固定为 Chromium、headless、isolated profile、
`1280×720` viewport。

Preflight 分别检查：

- Python Chromium 能否启动；
- 固定 Node Playwright MCP 能否执行真实 `browser_navigate`；
- `eval-web.mcpmark.ai` 与 arXiv 是否可达；
- X 直连状态（advisory，不因反爬单独阻止整个 Playwright job）。

正式 worker 会在自己的进程树内取消继承自 SSH/tmux 的 HTTP、HTTPS 和 ALL
proxy，避免指向登录客户端的 `127.0.0.1` 代理导致 Chromium
`ERR_PROXY_CONNECTION_FAILED`。这一操作不会影响 VS Code、Codex、父 shell 或
其他终端。

其中 `cloudflare_turnstile_challenge` 和 `birth_of_arvinxu` 受网页变化影响最大。
网站不可达、浏览器启动失败和服务端 5xx 应保留为 infrastructure error，不能当作
模型 utility 失败。

## 可选环境文件

正常 gpu3 直接运行流程不要求创建 `.mcp_env`。如需本地诊断，可以复制不含
secret 的
模板：

```bash
cp experiments/mcpmark_verified_utility/mcp_env.example \
  external/mcpmark/.mcp_env
chmod 600 external/mcpmark/.mcp_env
```

正式 runner 会把 Filesystem 和 Playwright 配置重新固定为 manifest 对应值，
防止旧 `.mcp_env` 把状态目录指向错误位置。

## 运行时边界

- 不要修改 `external/mcpmark` 的 tracked 文件；`validate` 要求 pinned checkout
  干净。
- 不要让其他程序使用实验启动的 PostgreSQL 容器或端口。
- 不要在正式运行中使用 `ALLOW_CONTAINER_PULL=1` 或
  `ALLOW_OLLAMA_PULL=1`；资产和模型应在提交前准备好。
- 不要把 Playwright 网站故障计入模型失败率。
