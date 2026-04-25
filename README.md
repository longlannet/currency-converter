# currency-converter

面向 OpenClaw 的 Frankfurter 汇率换算 skill，数据来自 European Central Bank (ECB)。

## 它能做什么

- 按每日可用 ECB 参考汇率换算货币
- 支持常见币种，如 USD、EUR、CNY、JPY、GBP、HKD 等
- 无需 API key
- 保持只读：不做交易、下单、账户访问或财务建议

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
python3 scripts/convert.py 100 USD CNY
python3 scripts/convert.py 1 EUR USD
python3 scripts/convert.py 100 USD USD
```

## 输出说明

脚本会输出：

- 原始金额与币种
- 换算后的金额与目标币种
- 汇率日期
- 查询时间
- 数据来源 Frankfurter API

## 说明

- Frankfurter 使用 ECB 参考汇率，周末或节假日通常返回最近一个工作日的汇率日期。
- 同币种和零金额换算会在本地直接返回，不请求 API。
- 如果环境缺失或状态异常，重新运行 `scripts/install.sh`。
