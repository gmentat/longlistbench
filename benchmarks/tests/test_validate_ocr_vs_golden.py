from benchmarks.validate_ocr_vs_golden import _compact, _identifier_found


def test_identifier_found_is_case_insensitive_for_ocr_names():
    ocr_text = "ANDRE A. ROMAN,MI license V9137114,11/27/1989"

    assert _identifier_found(
        "Andre A. Roman",
        ocr_text,
        _compact(ocr_text),
        field="name",
    )


def test_identifier_found_still_matches_compacted_values():
    ocr_text = "Policy: RVI 2401 7781"

    assert _identifier_found(
        "RVI24017781",
        ocr_text,
        _compact(ocr_text),
        field="policy_number",
    )
