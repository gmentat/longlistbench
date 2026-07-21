# Core Operations Generators

These scripts generate the 26 synthetic operational-document artifacts in LongListBench. Seeded generators reproduce the driver/MVR, multi-section IFTA, and loss-run ground truth. The other table templates render the committed synthetic ground truth. Together they make the relationship between target records and rendered documents auditable.

No production document is an input. Production references used during visual design review are intentionally excluded.

## Components

- `generate_driver_mvr.py`: driver rosters with sparse, cross-section MVR enrichment.
- `generate_ifta_multisection.py`: two deterministic multi-section IFTA packets.
- `generate_loss_runs.py`: three deterministic long-form loss runs.
- `render_operational_tables.py`: the remaining IFTA, driver-schedule, and vehicle-schedule layouts rendered from committed synthetic ground truth.

All commands default to `tmp/core_operations/` and never overwrite released data unless an explicit output directory is supplied.

```bash
python benchmarks/core_operations/generate_driver_mvr.py
python benchmarks/core_operations/generate_ifta_multisection.py
python benchmarks/core_operations/generate_loss_runs.py
python benchmarks/core_operations/render_operational_tables.py
```

The committed ground truth remains the release contract. Generator tests assert deterministic record counts and ensure that every non-null MVR enrichment value has a corresponding report in the rendered HTML.
