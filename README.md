# Auto CPA Register

## Automation Status

[![register-automation](https://github.com/linuxdoo/gpt-auto-register/actions/workflows/check_and_register.yml/badge.svg)](https://github.com/linuxdoo/gpt-auto-register/actions/workflows/check_and_register.yml)

如果仓库是私有仓库，这个 badge 和对应的 Actions 页面也只对有仓库访问权限的成员可见。

## Where To Check

- Actions 页面：查看 `register-automation` workflow 的最近一次运行结果、日志和步骤耗时
- Job Summary：每次运行结束后，会在 Actions 的 step summary 中显示
  - 当前 Sub2Api 数量
  - 触发阈值
  - 本次是否跳过
  - 本次计划注册数量

## Workflow

- 自动检查并按需注册：[.github/workflows/check_and_register.yml](./.github/workflows/check_and_register.yml)
- 检查脚本入口：[scripts/check_and_register.py](./scripts/check_and_register.py)
- 示例配置模板：[config.example.json](./config.example.json)
- 本地私密配置文件不入库：[`config.json`](./config.json) 已被 `.gitignore` 忽略

## GitHub Setup

首次推送到 `linuxdoo/gpt-auto-register` 之前，先确认以下内容：

- 提交 [config.example.json](./config.example.json)，不要提交本地真实 [config.json](./config.json)
- 提交 [zhuce5_cfmail_accounts.json](./zhuce5_cfmail_accounts.json) 前确认里面不含真实密钥；当前文件是分享安全示例
- 在仓库 `Settings -> Secrets and variables -> Actions` 中补齐需要的 `Secrets` / `Variables`

常用 `Secrets`：

- `DUCKMAIL_BEARER`
- `SUB2API_BASE_URL`
- `SUB2API_BEARER` 或 `SUB2API_EMAIL` + `SUB2API_PASSWORD`
- `CPA_BASE_URL`
- `CPA_MANAGEMENT_KEY`

常用 `Variables`：

- `SUB2API_MIN_COUNT`
- `TOPUP_BATCH_SIZE`
- `TOPUP_MAX_COUNT`
- `REGISTER_MAX_WORKERS`
- `REGISTER_CPA_CLEANUP`

## GitHub Secrets / Variables 对照表

下表按当前本地 `config.json` 的字段整理。原则是：

- 敏感值：放 `GitHub Secrets`
- 非敏感的开关、数量、路径：放 `GitHub Variables`
- 仅本地开发使用或在 `MODE=github` 下无效的项：不建议放 GitHub

| config.json 字段 | 建议放置 | GitHub 名称 | 说明 |
| --- | --- | --- | --- |
| `mode` | 不需要单独配置 | workflow 固定 `MODE=github` | GitHub Actions 已在 workflow 中固定为 `github` |
| `total_accounts` | Variable | `REGISTER_TOTAL_ACCOUNTS` | 仅手动直接注册时使用；自动补号流程主要看阈值配置 |
| `mail_provider` | Secret 或 Variable | `MAIL_PROVIDER` | 非敏感，但当前 workflow 按 Secret 读取也可继续保持 |
| `cfmail_config_path` | Variable | `CFMAIL_CONFIG_PATH` | 默认即可，通常不需要改 |
| `cfmail_profile` | Variable | `CFMAIL_PROFILE` | 默认 `auto` |
| `duckmail_api_base` | Secret 或 Variable | `DUCKMAIL_API_BASE` | 非敏感地址，放 Variable 更合理 |
| `duckmail_bearer` | Secret | `DUCKMAIL_BEARER` | 邮箱服务鉴权，必须放 Secret |
| `proxy` | 不建议在 GitHub 配置 | `PROXY` | `MODE=github` 下会被忽略 |
| `proxy_list_url` | 不建议在 GitHub 配置 | `PROXY_LIST_URL` | `MODE=github` 下会被忽略 |
| `proxy_list_bearer` | 不建议在 GitHub 配置 | `PROXY_LIST_BEARER` | `MODE=github` 下会被忽略 |
| `proxy_validate_enabled` | 不需要 | `PROXY_VALIDATE_ENABLED` | `MODE=github` 下代理关闭，通常无效 |
| `proxy_validate_timeout_seconds` | 不需要 | `PROXY_VALIDATE_TIMEOUT_SECONDS` | 同上 |
| `proxy_validate_workers` | 不需要 | `PROXY_VALIDATE_WORKERS` | 同上 |
| `proxy_validate_test_url` | 不需要 | `PROXY_VALIDATE_TEST_URL` | 同上 |
| `proxy_max_retries_per_request` | 不需要 | `PROXY_MAX_RETRIES_PER_REQUEST` | 同上 |
| `proxy_bad_ttl_seconds` | 不需要 | `PROXY_BAD_TTL_SECONDS` | 同上 |
| `proxy_retry_attempts_per_account` | Variable | `PROXY_RETRY_ATTEMPTS_PER_ACCOUNT` | 代码仍会用到账户级重试次数，建议保留 |
| `stable_proxy_file` | 不需要 | `STABLE_PROXY_FILE` | GitHub 临时环境，无持久意义 |
| `stable_proxy` | 不建议在 GitHub 配置 | `STABLE_PROXY` | `MODE=github` 下会被忽略 |
| `prefer_stable_proxy` | 不需要 | `PREFER_STABLE_PROXY` | `MODE=github` 下无效 |
| `output_file` | Variable | `REGISTER_OUTPUT_FILE` / `OUTPUT_FILE` | 默认即可，需要改输出文件名时再配 |
| `enable_oauth` | Variable | `ENABLE_OAUTH` | 一般保持 `true` |
| `oauth_required` | Variable | `OAUTH_REQUIRED` | 一般保持 `true` |
| `oauth_issuer` | Variable | `OAUTH_ISSUER` | 默认即可 |
| `oauth_client_id` | Secret 或 Variable | `OAUTH_CLIENT_ID` | 当前不是高敏值，但按 Secret 也没问题 |
| `oauth_redirect_uri` | Variable | `OAUTH_REDIRECT_URI` | 默认即可 |
| `ak_file` | Variable | `AK_FILE` | 默认即可 |
| `rk_file` | Variable | `RK_FILE` | 默认即可 |
| `token_json_dir` | Variable | `TOKEN_JSON_DIR` | 默认即可 |
| `cpa_base_url` | Secret 或 Variable | `CPA_BASE_URL` | 服务地址，按 Secret 读取可继续保持 |
| `cpa_management_key` | Secret | `CPA_MANAGEMENT_KEY` | 必须放 Secret |
| `auto_upload_cpa` | Variable | `AUTO_UPLOAD_CPA` | 是否自动上传到 CPA |
| `cpa_min_candidates` | Variable | `CPA_MIN_CANDIDATES` | CPA 相关阈值 |
| `upload_api_url` | 不单独配置 | 无 | 代码会由 `CPA_BASE_URL` 推导，通常不需要单独放 GitHub |
| `upload_api_token` | 不单独配置 | 无 | 代码会由 `CPA_MANAGEMENT_KEY` 推导，通常不需要单独放 GitHub |
| `cpa_cleanup_enabled` | Variable | `REGISTER_CPA_CLEANUP` | workflow 里使用注册前清理开关 |
| `sub2api_base_url` | Secret 或 Variable | `SUB2API_BASE_URL` | 接口地址，建议至少配置 |
| `sub2api_bearer` | Secret | `SUB2API_BEARER` | 有 Bearer 时优先使用 |
| `sub2api_email` | Secret | `SUB2API_EMAIL` | 没有 Bearer 时可回退邮箱登录 |
| `sub2api_password` | Secret | `SUB2API_PASSWORD` | 同上，必须 Secret |
| `auto_upload_sub2api` | Variable | `AUTO_UPLOAD_SUB2API` | 是否自动回传 Sub2Api |
| `sub2api_group_ids` | Variable | `SUB2API_GROUP_IDS` | 多个值用逗号，如 `2,4` |
| `sub2api_min_candidates` | Variable | `SUB2API_MIN_CANDIDATES` | Sub2Api 内部候选阈值 |
| `sub2api_proxy_id` | Variable | `SUB2API_PROXY_ID` | GitHub 无代理模式下通常保留 `0` |
| `sub2api_proxy_name` | Variable | `SUB2API_PROXY_NAME` | 可留空 |
| `sub2api_auto_assign_proxy` | Variable | `SUB2API_AUTO_ASSIGN_PROXY` | GitHub 无代理模式下通常设 `false` |

### 最小必配

如果你只想先把自动补号跑起来，至少配置这些：

- `Secrets`
  - `DUCKMAIL_BEARER`
  - `SUB2API_BASE_URL`
  - `SUB2API_BEARER` 或 `SUB2API_EMAIL` + `SUB2API_PASSWORD`
- `Variables`
  - `SUB2API_MIN_COUNT`
  - `TOPUP_BATCH_SIZE`
  - `TOPUP_MAX_COUNT`
  - `REGISTER_MAX_WORKERS`

### 建议不要直接从本地同步到 GitHub 的字段

- 所有本地代理相关字段：`proxy`、`proxy_list_url`、`proxy_list_bearer`、`stable_proxy`
- 本地运行产物路径如果没有特别需求，也不要自定义
- `upload_api_url`、`upload_api_token` 这类可由其他字段推导出的字段，不必重复配置

## Notes

- 手动触发 workflow 时，可以填写 `manual_total_accounts` 强制指定本次注册数量
- 定时触发时，会先检查 `sub2api` 数量，低于阈值才运行注册
- 当前 GitHub Actions 运行模式固定为 `MODE=github`，不会使用本地代理或代理池配置
