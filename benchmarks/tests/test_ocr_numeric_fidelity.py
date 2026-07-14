from benchmarks.validate_ocr_numeric_fidelity import (
    baseline_payload,
    check_sample,
    count_checked_numeric_fields,
    numeric_value_found,
)


def test_numeric_fidelity_checks_nested_numeric_fields():
    records = [
        {
            "incident_number": "INC-100",
            "financial_breakdown": {
                "paid": 1234.56,
            },
        }
    ]

    misses = check_sample(records, "INC-100 paid $1,111.56", min_abs=10)

    assert misses == [
        {
            "record_index": 0,
            "record_key": "INC-100",
            "field": "financial_breakdown.paid",
            "value": 1234.56,
        }
    ]


def test_numeric_fidelity_requires_negative_sign_or_parentheses():
    assert numeric_value_found(-1234.56, "tax due ($1,234.56)")
    assert numeric_value_found(-1234.56, "tax due -$1,234.56")
    assert not numeric_value_found(-1234.56, "tax due $1,234.56")


def test_numeric_fidelity_does_not_accept_negative_for_positive_value():
    assert numeric_value_found(1234.56, "tax due $1,234.56")
    assert not numeric_value_found(1234.56, "tax due ($1,234.56)")
    assert not numeric_value_found(1234.56, "tax due -$1,234.56")


def test_audited_baseline_is_deterministic_and_counts_checked_fields():
    records = [{"claim_number": "A", "paid": 100, "reserve": 5}]
    misses = check_sample(records, "claim A paid 101", min_abs=10)

    payload = baseline_payload(
        {"sample": misses, "clean": []},
        min_abs=10,
        checked_numeric_fields=count_checked_numeric_fields(records, min_abs=10),
    )

    assert payload == {
        "schema_version": 1,
        "min_abs": 10,
        "checked_numeric_fields": 1,
        "documents_with_misses": 1,
        "total_misses": 1,
        "misses": {
            "sample": [
                {
                    "record_index": 0,
                    "record_key": "A",
                    "field": "paid",
                    "value": 100.0,
                }
            ]
        },
    }
