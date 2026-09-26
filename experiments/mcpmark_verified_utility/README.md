# MCPMark Verified utility experiment

这个目录实现一个不需要 GitHub/Notion 凭据的 MCPMark Verified utility 对照实验。
正式运行方式是在 `gpu3` 上直接使用四张 NVIDIA A40，不经过 Slurm。

## 冻结实验设计

| Service | 任务数 | 4 模型 × 2 条件后的轨迹数 |
|---|---:|---:|
| Filesystem | 20 | 160 |
| PostgreSQL | 20 | 160 |
| Playwright | 4 | 32 |
| 合计 | 44 | 352 |

实验名称为：

> **MCPMark Verified deployment-feasible 3-service subset**

不使用 GitHub、Notion 或 Playwright WebArena。完整选择规则见
[`CASE_SELECTION.md`](./CASE_SELECTION.md)。

冻结配置：

- MCPMark commit：`cd45b7f57923b9b3985467f5139927575f83141c`
- suite：`standard` / L3
- models：4
- conditions：`original`、`safety`
- `k=1`
- temperature：`0`
- max tokens：`32768`
- max turns：`100`
- per-task timeout：`3600s`

四个 Ollama 模型为：

| Label | Ollama model | Context | A40 数量 |
|---|---|---:|---:|
| `llama31_8b` | `llama3.1:8b` | 131072 | 1 |
| `llama31_70b` | `llama3.1:70b` | 131072 | 2 |
| `qwen3_8b` | `qwen3:8b` | 40960 | 1 |
| `qwen3_32b` | `qwen3:32b` | 40960 | 1 |

Safety prompt 来自：

```text
experiments/mcpmark_verified_utility/safety_prompt.txt
```

## 直接运行架构

[`run_gpu3_experiment.sh`](./run_gpu3_experiment.sh) 是正式入口。它不调用
`sbatch`，而是在本机调度 12 个单元：

```text
4 models × 3 services = 12 workers
```

每个 worker：

1. 独占分配给它的一张或两张 A40；
2. 启动一个只监听 loopback 唯一端口的 Ollama；
3. 仅在 worker 子进程树中取消 `HTTP_PROXY`、`HTTPS_PROXY` 和
   `ALL_PROXY` 的大小写变量；
4. 通过 Ollama load-only API 预加载完整模型，冷加载最多等待 1260 秒；
5. 完成 endpoint、tool call、CUDA、context 和完整 GPU offload 检查；
6. 在同一个 Ollama endpoint 和同一个 model artifact 上依次运行
   `original,safety`；
7. 完成后清理 Ollama、MCP/browser 子进程和专用 PostgreSQL 容器。

load-only 预热把大模型冷加载与 180 秒 endpoint 能力检查分开。Qwen3 的工具调用
能力检查使用 512 token，避免默认 thinking 在 128 token 上限处造成假阴性；正式
trajectory 仍严格使用上面冻结的 `temperature=0`、`max tokens=32768` 和默认
reasoning 配置。

Playwright MCP 的相对输出文件固定写入
`/tmp/mcpmark-playwright-mcp-<uid>/server-<pid>`，不能写入 pinned
`external/mcpmark` checkout。包装器同时设置 `PLAYWRIGHT_MCP_OUTPUT_DIR` 并把
MCP 进程的工作目录切换到这个目录：前者覆盖服务端自动命名的输出，后者覆盖模型在
`browser_snapshot(filename=...)` 等调用中显式指定的相对文件名。否则一个
Playwright 题生成的文件会让并发启动的 Filesystem/PostgreSQL worker 把 checkout
判定为 dirty。

取消代理只发生在 scheduler 启动的 worker 及其后代中。它不会修改当前 tmux
shell、`~/.bashrc`、VS Code、Codex 或用户级代理配置。环境安装/下载脚本仍可使用
调用者已有的代理。

中央调度器同时占定 GPU 和 service。同一 service 永不并发，不同 service 可以在
GPU 不重叠时并行。这避免 Filesystem 初始化竞争、PostgreSQL 状态干扰和
Playwright 公网页面并发限流。

任一单元失败后，其 GPU 和 service 都会被释放，其他单元继续运行。再次使用相同
`EXP` 启动时，正常结果自动复用，infrastructure error 自动重试；不使用
`--force-rerun`。

## 1. 一次性环境和资产准备

从仓库根目录执行：

```bash
bash experiments/mcpmark_verified_utility/setup_environment.sh
bash experiments/mcpmark_verified_utility/prepare_service_assets.sh
```

严格检查：

```bash
bash experiments/mcpmark_verified_utility/setup_environment.sh --check-only
bash experiments/mcpmark_verified_utility/prepare_service_assets.sh --check-only

PY=experiments/mcpmark_verified_utility/.venv/bin/python
"$PY" experiments/mcpmark_verified_utility/run_experiment.py validate
```

这些步骤不需要 GitHub/Notion API。Service 状态机制见
[`SERVICE_SETUP.md`](./SERVICE_SETUP.md)。

## 2. 检查四个模型

模型必须提前存在于 gpu3 可见的 Ollama store 中：

```bash
ollama show llama3.1:8b
ollama show llama3.1:70b
ollama show qwen3:8b
ollama show qwen3:32b
```

正式 worker 不会临时下载模型。

## 3. 取消旧 Slurm 作业

此前已经提交了 job `3799–3822`。先在能够访问 Slurm 的登录节点执行：

```bash
scancel {3799..3822}
squeue -u "$USER"
```

确认这些 job 已不存在后再进入 gpu3。不要让旧 job 和直接运行同时执行；它们会
争用 GPU 和共享 service state。

旧目录
`runs/mcpmark_verified_utility_main` 保留为提交审计记录，不要把它用作新的直接
运行目录。

## 4. 在 gpu3 上正式启动

建议使用 `tmux`，避免 SSH 断开终止全部 worker：

```bash
ssh gpu3
cd /path/to/LPS-Bench
tmux new -s mcpmark-utility
```

在 tmux 中执行：

```bash
export EXP="$PWD/runs/mcpmark_verified_utility_gpu3_main_v3"
export MCPMARK_CONFIRM_NO_SLURM_JOBS=1

bash experiments/mcpmark_verified_utility/run_gpu3_experiment.sh --check-only
bash experiments/mcpmark_verified_utility/run_gpu3_experiment.sh
```

第一条只检查 gpu3、四张 A40、冻结输入、实验局部代理策略和本地 Podman runtime，
不会启动模型或 benchmark；通过后再执行第二条正式启动。

`runs/mcpmark_verified_utility_gpu3_main` 和
`runs/mcpmark_verified_utility_gpu3_main_v2` 是 2026-07-30 的失败诊断轮。
v2 暴露并修复了 PostgreSQL `pipx` wrapper、70B 冷加载和 Qwen3 smoke budget
问题；修复后 runner、worker 和 scheduler 的 hash 已改变，不能复用这些目录，
必须使用上面的全新 `EXP`。

正式入口会检查：

- 当前短 hostname 必须是 `gpu3`；
- GPU `0,1,2,3` 必须都存在且都是 A40；
- 启动时四张卡上没有其他 compute process；
- environment、service assets 和冻结输入全部通过；
- PostgreSQL Podman graphroot 位于 gpu3 的本地 `/var/tmp`，不是 NFS home；
- plan 恰好包含 352 条 trajectory；
- 使用全新的直接运行目录，不能混用旧 Slurm `EXP`。

Podman 的用户级默认配置不会被修改。正式入口会为当前 `EXP` 生成：

```text
$EXP/runtime/podman/storage.conf
```

实际 image/layer 存储位于 gpu3 本地
`/var/tmp/mcpmark-verified-utility-podman-<uid>/<exp-id>`，运行态目录位于
`/run/user/<uid>/mcpmark-verified-utility-<exp-id>`。这些设置只传给本实验的
容器命令。

如 gpu3 的物理 GPU 编号不同，可显式设置：

```bash
export MCPMARK_GPU_IDS=0,1,2,3
```

## 5. 查看状态

另开一个 SSH/tmux 窗口：

```bash
nvidia-smi

find "$EXP/status" -maxdepth 1 -type f | sort
tail -f "$EXP"/logs/direct/*.out
```

每个单元写入：

```text
status/<model>_<service>_both.runtime
status/<model>_<service>_both.done
status/<model>_<service>_both.failed
```

`.runtime` 只表示 worker 已写入运行配置，不代表该单元成功。只有 `.done` 和
调度器输出的 `complete model=...` 才表示一个单元完成。

直接调度日志位于：

```text
logs/direct/<model>_<service>_both.out
logs/direct/<model>_<service>_both.err
```

Ollama 详细日志位于：

```text
logs/<model>_<service>_both_ollama_<pid>.log
```

全部成功时会生成：

```text
$EXP/direct_run.done
```

如果存在 `$EXP/direct_run.failed`，且 runner/worker/scheduler/config 均未改变，
修复对应 `.err` 中的基础设施问题后，保持同一个 `EXP` 再运行入口脚本即可续跑。
如果代码或冻结配置发生变化，hash contract 会拒绝混跑，此时必须换新 `EXP`。

## 6. 汇总结果

只在 `direct_run.done` 出现后运行：

```bash
"$PY" experiments/mcpmark_verified_utility/summarize_results.py \
  --results-root "$EXP/results"
```

输出：

```text
$EXP/results/summary.json
$EXP/results/summary.md
```

汇总器要求所有预期结果都通过 sidecar、prompt、model artifact、endpoint 和
configuration 审计，否则返回非零。诊断未完成实验时才使用：

```bash
"$PY" experiments/mcpmark_verified_utility/summarize_results.py \
  --results-root "$EXP/results" \
  --allow-incomplete
```

主指标是每个模型内的三服务等权 macro。Task micro 是次要描述性指标；missing 和
infrastructure error 不会被当成模型任务失败。

## 运行边界

- 不要修改 `external/mcpmark` 的 tracked 文件。
- 不要在运行中改变模型、prompt、manifest、runner、worker 或 GPU 列表。
- 不要设置 `ALLOW_OLLAMA_PULL=1` 或 `ALLOW_CONTAINER_PULL=1`。
- 不要让其他进程使用分配给实验的 GPU 或 loopback 端口 `24000–24011`。
- Playwright 公网页面不可冻结；站点、浏览器或服务端故障应修复后重跑对应 pair，
  不能计作 safety prompt 导致的 utility 下降。
