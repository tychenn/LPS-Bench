# Frozen MCP-Bench utility cases

- Upstream revision: `7a8eaeae83a842a2949080acc5473f65e1569daf`
- Algorithm: `mcpbench-deployable-coverage-v2`
- Seed: `lps-mcpbench-utility-2026-07-31`
- Total: 20 tasks
- Credentialed servers excluded: BioMCP, Google Maps, Hugging Face, NASA Data, National Parks
- Other deployment exclusions: OSINT Intelligence (requires undeclared host binaries (whois, dnsrecon, and dnstwist))
- Distractor servers: disabled

| Stratum | Task ID | Required servers | Source |
|---|---|---|---|
| single | `fruityvice_000` | FruityVice | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `openapi_explorer_000` | OpenAPI Explorer | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `movie_recommender_001` | Movie Recommender | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `huge_icons_001` | Huge Icons | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `car_price_evaluator_001` | Car Price Evaluator | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `game_trends_001` | Game Trends | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `context7_001` | Context7 | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `metropolitan_museum_001` | Metropolitan Museum | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `okx_exchange_000` | OKX Exchange | `tasks/mcpbench_tasks_single_runner_format.json` |
| single | `time_mcp_000` | Time MCP | `tasks/mcpbench_tasks_single_runner_format.json` |
| two_server | `unit_converter_math_mcp_000` | Unit Converter + Math MCP | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| two_server | `reddit_dex_paprika_001` | Reddit + DEX Paprika | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| two_server | `wikipedia_paper_search_001` | Wikipedia + Paper Search | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| two_server | `nixos_context7_000` | NixOS + Context7 | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| two_server | `scientific_computing_math_mcp_001` | Scientific Computing + Math MCP | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| two_server | `metropolitan_museum_wikipedia_000` | Metropolitan Museum + Wikipedia | `tasks/mcpbench_tasks_multi_2server_runner_format.json` |
| three_server | `medical_calculator_wikipedia_fruityvice_000` | Medical Calculator + Wikipedia + FruityVice | `tasks/mcpbench_tasks_multi_3server_runner_format.json` |
| three_server | `paper_search_call_for_papers_wikipedia_000` | Paper Search + Call for Papers + Wikipedia | `tasks/mcpbench_tasks_multi_3server_runner_format.json` |
| three_server | `metropolitan_museum_huge_icons_wikipedia_001` | Metropolitan Museum + Huge Icons + Wikipedia | `tasks/mcpbench_tasks_multi_3server_runner_format.json` |
| three_server | `medical_calculator_wikipedia_fruityvice_001` | Medical Calculator + Wikipedia + FruityVice | `tasks/mcpbench_tasks_multi_3server_runner_format.json` |

## Source file checksums

- `73304aec75c175fb1b65c36352aaece9975caa14f5b992a95882cc2863905b3b  tasks/mcpbench_tasks_single_runner_format.json`
- `9517a63ac0bc3b3ed70a465489c8e43867386180c6907648e9e2e6924f26e878  tasks/mcpbench_tasks_multi_2server_runner_format.json`
- `0e1f63c370e058e2ad154359363e12389069d76b874053c42048d30d9928cf7b  tasks/mcpbench_tasks_multi_3server_runner_format.json`
