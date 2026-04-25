# currency-converter

面向 OpenClaw 的多源汇率换算 skill。默认使用免费、无 API key、更新较快的参考汇率源，并保留 Frankfurter / ECB 每日官方参考汇率模式。

> 所有输出都只是参考汇率，不是交易级报价，也不构成财务建议。

## 它能做什么

- 按快速免费源换算货币，默认无需 API key
- 查询 USD/CNY、EUR/USD、JPY/CNY 等常见币种汇率
- 在快速源不可用时自动 fallback
- 显式查询 Frankfurter / ECB 每日参考汇率
- 处理同币种和零金额换算，不浪费 API 请求

## 数据源

| Source | 命令参数 | 更新频率 | API key | 说明 |
| --- | --- | --- | --- | --- |
| 自动快速源 | `--source auto` / 默认 | 优先 5 分钟级，失败后 fallback | 不需要 | fxapi.app → MoneyConvert → ECB |
| fxapi.app | `--source fxapi` | 标称 5 分钟 | 不需要 | 接入简单，适合快速查询 |
| MoneyConvert | `--source moneyconvert` | 标称 5 分钟 | 不需要 | CDN JSON，作为备用快速源 |
| Frankfurter / ECB | `--source ecb` | ECB 工作日每日更新 | 不需要 | 官方参考属性强，但非实时 |

## 安装

```bash
bash scripts/install.sh
```

## 校验

```bash
bash scripts/check.sh
```

离线或只想检查本地文件时，可跳过网络 smoke test：

```bash
RUN_SMOKE=0 bash scripts/check.sh
```

## 常用命令

请在 skill 根目录运行：

```bash
# 默认：快速源自动 fallback
python3 scripts/convert.py 100 USD CNY

# 指定快速源
python3 scripts/convert.py 100 USD CNY --source fxapi
python3 scripts/convert.py 100 USD CNY --source moneyconvert

# 指定 ECB 每日参考汇率
python3 scripts/convert.py 100 USD CNY --source ecb

# 本地处理，不请求 API
python3 scripts/convert.py 100 USD USD
python3 scripts/convert.py 0 EUR GBP
```

## 输出说明

脚本会输出：

- 原始金额与币种
- 换算后的金额与目标币种
- 单位汇率（如 `1 USD = ... CNY`）
- 汇率时间 / 日期
- 查询时间
- 数据来源与来源模式
- 数据新鲜度说明
- 如发生 fallback，会显示备用源失败原因

## 注意

- 默认快速源不是官方央行报价，也不是交易级报价。
- `fxapi.app` 与 `MoneyConvert` 标称 5 分钟更新，但长期稳定性和数据源透明度不如老牌付费/官方数据源。
- `Frankfurter / ECB` 是每日参考汇率，周末或节假日通常返回最近一个工作日的汇率日期。
- 如果需要生产级、审计级或交易级数据，应接入更成熟的付费源或官方授权数据源。
