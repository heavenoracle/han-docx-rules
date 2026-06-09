# han-docx-rules

[中文](#中文) | [English](#english)

## 中文

`han-docx-rules` 为中文学术 DOCX 文档提供可审计、可复用的质量检查配置。规则集由
[han-docx-lint](https://github.com/heavenoracle/han-docx-lint) 执行，也可通过
[han-docx-action](https://github.com/heavenoracle/han-docx-action) 集成到 GitHub CI。

该项目解决配置复用问题：检查引擎保持通用，课程、实验室和开放文档项目可以选择并审查
适合自己的规则集，无需复制检查代码。

### 规则集

| 配置 | 用途 |
| --- | --- |
| `profiles/general-quality.json` | 通用中文学术文档质量检查 |
| `profiles/coursework.json` | 课程论文草稿，强调占位文本和参考文献 |
| `profiles/journal-draft.json` | 投稿前草稿，增加非正式措辞提示 |

```bash
han-docx-lint paper.docx --config profiles/general-quality.json
python tools/validate_profiles.py
```

这些规则集是通用质量检查配置，**不代表任何学校、期刊或标准化组织的官方规范**。
使用者应根据实际提交要求审查并调整配置。

## English

`han-docx-rules` provides auditable, reusable quality profiles for Chinese
academic DOCX files. Profiles run with
[han-docx-lint](https://github.com/heavenoracle/han-docx-lint) and can be used
in CI through [han-docx-action](https://github.com/heavenoracle/han-docx-action).

These profiles are general-purpose quality checks. They do **not** claim
compliance with any university, journal, or standards body.

## Profile contract

- JSON encoded as UTF-8.
- `version` is currently `1`.
- Built-in rule IDs and configuration behavior are defined by `han-docx-lint`.
- Custom pattern rules must document intent and likely false positives.
- Every profile must pass `python tools/validate_profiles.py`.

Profiles should be reviewed like code before use, especially when they are
changed by an untrusted pull request. Custom regular expressions are executed
against document text by the checking engine.

## License

MIT
