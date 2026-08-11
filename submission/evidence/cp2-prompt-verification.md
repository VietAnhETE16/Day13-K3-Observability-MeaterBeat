# CP2 prompt version verification

Xác minh qua Langfuse API ngày 2026-08-11, dùng cùng input:

```text
How do metrics, traces, and logs work together?
```

| Trường hợp | Trace ID | Prompt label | Prompt version | Prompt source |
|---|---|---|---:|---|
| Baseline | `9d94ef9507a308f99eb4db0bac40e626` | `baseline` | 1 | `langfuse` |
| Candidate | `e012eb73cc1c300971287b3ab7766a39` | `candidate` | 2 | `langfuse` |
| Production chuyển sang v2 | `8712e45d8f16ec5f981e02e05aa366e2` | `production` | 2 | `langfuse` |
| Production rollback về v1 | `c724dd6021022bc5e7058ac323246190` | `production` | 1 | `langfuse` |

Trạng thái cuối:

- Version 1: labels `baseline`, `production`.
- Version 2: labels `candidate`, `latest`.
- Label `production` resolve về version 1.

Evidence UI còn phải chụp trong phiên đăng nhập Langfuse:

- Danh sách hai prompt version và labels.
- Trạng thái `production` trên version 1 sau rollback.
