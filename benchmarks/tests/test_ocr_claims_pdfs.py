from benchmarks.ocr_claims_pdfs import ocr_user_prompt


def test_layout_table_mode_forbids_csv_normalization():
    prompt = ocr_user_prompt("layout")

    assert "Do not convert tables to CSV" in prompt
    assert "preserve the visible table layout" in prompt


def test_csv_table_mode_keeps_existing_prompt_contract():
    prompt = ocr_user_prompt("csv")

    assert "Format tables as CSV" in prompt
