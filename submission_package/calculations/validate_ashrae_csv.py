#!/usr/bin/env python3
"""Validate ASHRAE CSV tables in this repository.

Checks performed per table:
- Required header columns
- Expected data row count
- Consistent number of columns in data rows
- Numeric parse for numeric fields
- Table-specific domain checks (months, latitudes, facings)
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass
class TableSpec:
    name: str
    path: Path
    header: list[str]
    expected_rows: int
    first_col_validator: Callable[[str], bool]
    second_col_validator: Callable[[str], bool] | None = None
    numeric_start_col: int = 1


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _read_table_rows(path: Path, header: list[str]) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        all_rows = list(csv.reader(f))

    header_idx = -1
    for i, row in enumerate(all_rows):
        if row == header:
            header_idx = i
            break

    if header_idx == -1:
        raise ValueError(f"Header not found in {path}")

    data_rows: list[list[str]] = []
    for row in all_rows[header_idx + 1 :]:
        if not row:
            continue
        # Skip spacer rows like ',' that appear as [''] or ['', ...]
        if all(cell.strip() == "" for cell in row):
            continue
        data_rows.append([cell.strip() for cell in row])

    return all_rows[header_idx], data_rows


def _validate_table(spec: TableSpec) -> list[str]:
    errors: list[str] = []

    if not spec.path.exists():
        return [f"{spec.name}: missing file {spec.path}"]

    try:
        found_header, data_rows = _read_table_rows(spec.path, spec.header)
    except Exception as exc:  # noqa: BLE001
        return [f"{spec.name}: failed reading table ({exc})"]

    if found_header != spec.header:
        errors.append(f"{spec.name}: header mismatch")

    if len(data_rows) != spec.expected_rows:
        errors.append(
            f"{spec.name}: expected {spec.expected_rows} rows, found {len(data_rows)}"
        )

    for idx, row in enumerate(data_rows, start=1):
        if len(row) != len(spec.header):
            errors.append(
                f"{spec.name}: row {idx} has {len(row)} columns, expected {len(spec.header)}"
            )
            continue

        if not spec.first_col_validator(row[0]):
            errors.append(f"{spec.name}: row {idx} first column invalid value '{row[0]}'")

        if spec.second_col_validator and not spec.second_col_validator(row[1]):
            errors.append(f"{spec.name}: row {idx} second column invalid value '{row[1]}'")

        for j, value in enumerate(row[spec.numeric_start_col:], start=spec.numeric_start_col + 1):
            if not _is_float(value):
                errors.append(
                    f"{spec.name}: row {idx} col {j} not numeric ('{value}')"
                )

    return errors


def _in_set(values: Iterable[str]) -> Callable[[str], bool]:
    value_set = set(values)
    return lambda x: x in value_set


def main() -> int:
    base = Path(__file__).resolve().parent / "ASHRAE_Tables"

    table9_months = ["Dec", "Jan/Nov", "Feb/Oct", "Mar/Sept", "Apr/Aug", "May/Jul", "Jun"]
    table9_lats = ["0", "8", "16", "24", "32", "40", "48", "56", "64"]
    table9_first_col_values = [f"{lat}" for lat in table9_lats]

    table12_months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    table14_facings = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "HOR",
    ]

    specs = [
        TableSpec(
            name="Table9",
            path=base / "Table9_CLTD_Correction_Latitude_Month.csv",
            header=[
                "Lat",
                "Month",
                "N",
                "NNE_NNW",
                "NE_NW",
                "ENE_WNW",
                "E_W",
                "ESE_WSW",
                "SE_SW",
                "SSE_SSW",
                "S",
                "HOR",
            ],
            expected_rows=63,
            first_col_validator=_in_set(table9_first_col_values),
            second_col_validator=_in_set(table9_months),
            numeric_start_col=2,
        ),
        TableSpec(
            name="Table12",
            path=base / "Table12_Maximum_Solar_Heat_Gain_Factor_Externally_Shaded_Glass.csv",
            header=[
                "Month",
                "N",
                "NNE_NNW",
                "NE_NW",
                "ENE_WNW",
                "E_W",
                "ESE_WSW",
                "SE_SW",
                "SSE_SSW",
                "S",
                "ALL_LAT_HOR",
            ],
            expected_rows=12,
            first_col_validator=_in_set(table12_months),
            numeric_start_col=1,
        ),
        TableSpec(
            name="Table14",
            path=base / "Table14_Cooling_Load_Factors_Glass_Interior_Shading.csv",
            header=[
                "Fenestration_Facing",
                "H0100",
                "H0200",
                "H0300",
                "H0400",
                "H0500",
                "H0600",
                "H0700",
                "H0800",
                "H0900",
                "H1000",
                "H1100",
                "H1200",
                "H1300",
                "H1400",
                "H1500",
                "H1600",
                "H1700",
                "H1800",
                "H1900",
                "H2000",
                "H2100",
                "H2200",
                "H2300",
                "H2400",
            ],
            expected_rows=17,
            first_col_validator=_in_set(table14_facings),
            numeric_start_col=1,
        ),
    ]

    all_errors: list[str] = []
    for spec in specs:
        errors = _validate_table(spec)
        if errors:
            all_errors.extend(errors)

    # Extra domain check for Table9 month cycle per latitude.
    table9_path = base / "Table9_CLTD_Correction_Latitude_Month.csv"
    if table9_path.exists():
        _, rows = _read_table_rows(
            table9_path,
            [
                "Lat",
                "Month",
                "N",
                "NNE_NNW",
                "NE_NW",
                "ENE_WNW",
                "E_W",
                "ESE_WSW",
                "SE_SW",
                "SSE_SSW",
                "S",
                "HOR",
            ],
        )
        by_lat: dict[str, list[str]] = {}
        for row in rows:
            by_lat.setdefault(row[0], []).append(row[1])
        for lat, months in by_lat.items():
            if months != table9_months:
                all_errors.append(
                    f"Table9: month sequence mismatch for lat {lat}: {months}"
                )

    if all_errors:
        print("Validation FAILED:")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print("Validation OK: Table9, Table12, Table14")
    return 0


if __name__ == "__main__":
    sys.exit(main())
