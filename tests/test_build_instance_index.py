import json

from benchmarks.build_instance_index import build_instance_index


def test_instance_index_uses_portable_dataset_label(tmp_path) -> None:
    dataset_dir = tmp_path / "data"
    dataset_dir.mkdir()
    (dataset_dir / "manifest.json").write_text(
        json.dumps({"instances": []}),
        encoding="utf-8",
    )

    index = build_instance_index(dataset_dir)

    assert index["dataset_dir"] == "data"
    assert str(tmp_path) not in json.dumps(index)
