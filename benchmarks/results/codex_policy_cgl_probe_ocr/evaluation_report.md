# Codex Policy CGL OCR Probe

Generated: 2026-06-25

This is a narrow diagnostic run, not a full current-corpus leaderboard. The run uses the current `mixed_cgl_040_001` OCR transcript, the public policy field contract, and a Codex workspace with code execution enabled while the benchmark repository is denied. The workspace did not include ground-truth files.

| Sample | Input | Model/protocol | Gold records | Predicted records | F1 | Recall | Precision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `mixed_cgl_040_001` | Gemini OCR transcript | Codex GPT-5.5 agentic sandbox | 619 | 619 | 92.7% | 89.9% | 95.6% |

The model recovered the full record count. Most remaining loss is in exact material-clause fields; schedule, form, endorsement, and premium records are largely recovered by programmatic inspection of the OCR transcript.
