#!/usr/bin/env python3
"""
Data profile generator for analysis projects.

Writes a Markdown data-quality profile of the raw data, so the initial-analysis
notebook can start from known facts instead of rediscovering them.

Usage (from the project root):
    .venv/bin/python scripts/profile-data.py                     # every data file in data/raw/
    .venv/bin/python scripts/profile-data.py data/raw/file.csv   # specific file(s)
    .venv/bin/python scripts/profile-data.py --dictionary data/raw/columns.csv
    .venv/bin/python scripts/profile-data.py --output reports/data-profile.md

A file whose name contains "description", "dictionary", "metadata", "codebook"
or "schema" is treated as a data dictionary (field name, description) and is
matched against the columns instead of being profiled.

The profile states facts and flags things worth checking. It does not
interpret them; a flagged column may be perfectly fine.

Requires only pandas and numpy (openpyxl / pyarrow for Excel / Parquet files).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

DATA_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".parquet", ".json"}
DICTIONARY_HINTS = ("description", "dictionary", "metadata", "codebook", "schema")
ENCODINGS = ("utf-8", "cp1252", "latin-1")  # latin-1 never fails, so it is the last resort

LOW_CARDINALITY = 25      # show the value distribution for columns with at most this many values
TOP_N = 6                 # values shown per low-cardinality column
MOSTLY_MISSING = 0.50
DOMINANT_VALUE = 0.99
OUTLIER_SHARE_FLAG = 0.05
MAX_EXAMPLE_LEN = 40

PLACEHOLDER_RE = re.compile(
    r"^\s*(?:([A-Za-z*#?.\-_])\1{2,}|n/?a|nan|null|none|nil|unknown|unk|missing|"
    r"not available|not applicable|tbd|undefined|\?+|-+|0000-00-00)\s*$",
    re.IGNORECASE,
)
MOJIBAKE_RE = re.compile(r"Ã[\u0080-\u00ff]|Â[\u0080-\u00ff]|â€")
SENTINELS = {-1, -9, -99, -999, -9999, 99, 999, 9999, 99999}


# --------------------------------------------------------------------------- reading


def sniff_separator(path: Path, encoding: str) -> str:
    with open(path, encoding=encoding, errors="replace") as fh:
        sample = fh.read(65536)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_table(path: Path) -> tuple[pd.DataFrame, str]:
    """Read a data file, returning (dataframe, encoding or format note)."""
    ext = path.suffix.lower()
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(path), "excel"
    if ext == ".parquet":
        return pd.read_parquet(path), "parquet"
    if ext == ".json":
        return pd.read_json(path), "json"

    last_error: Exception | None = None
    for encoding in ENCODINGS:
        try:
            sep = "\t" if ext == ".tsv" else sniff_separator(path, encoding)
            return pd.read_csv(path, sep=sep, encoding=encoding, low_memory=False), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error  # pragma: no cover


def is_dictionary_file(path: Path) -> bool:
    name = path.name.lower()
    return any(hint in name for hint in DICTIONARY_HINTS) and path.stat().st_size < 2_000_000


def discover_files(raw_dir: Path) -> list[Path]:
    files = []
    for p in sorted(raw_dir.rglob("*")):
        rel = p.relative_to(raw_dir)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if p.is_file() and p.suffix.lower() in DATA_EXTENSIONS:
            files.append(p)
    return files


def load_dictionary(path: Path) -> dict[str, str]:
    df, _ = read_table(path)
    if df.shape[1] < 2:
        return {}
    out = {}
    for field, desc in zip(df.iloc[:, 0], df.iloc[:, 1]):
        if pd.isna(field):
            continue
        desc = "" if pd.isna(desc) else str(desc)
        out[normalise_name(str(field))] = re.sub(r"^[\s:\-]+", "", desc).strip()
    return out


def normalise_name(name: str) -> str:
    return re.sub(r"[^0-9a-z]", "", name.casefold())


# --------------------------------------------------------------------------- formatting


def md(text: object, limit: int | None = MAX_EXAMPLE_LEN) -> str:
    s = str(text).replace("\n", " ").replace("\r", " ").replace("|", "\\|")
    if limit and len(s) > limit:
        s = s[: limit - 1] + "…"
    return s


def num(x: float | int | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    if isinstance(x, (int, np.integer)) or float(x).is_integer():
        return f"{int(x):,}"
    return f"{x:,.{digits}f}"


def show(v: object) -> str:
    """Display a value; floats are trimmed to 6 significant digits (hides float32 noise like 0.039999999)."""
    if isinstance(v, (float, np.floating)):
        return f"{v:.6g}"
    return str(v)


def pct(part: float, whole: float) -> str:
    if whole == 0:
        return "–"
    share = 100 * part / whole
    if share == 0:
        return "0%"
    if share < 0.1:
        return "<0.1%"
    return f"{share:.1f}%"


def count_pct(part: int, whole: int) -> str:
    return "–" if part == 0 else f"{part:,} ({pct(part, whole)})"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


# --------------------------------------------------------------------------- column checks


def kind_of(s: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    return "text"


def detect_datetime(nn: pd.Series) -> dict | None:
    """Return date info if a text column holds dates, else None."""
    if nn.empty:
        return None
    sample = nn.sample(min(len(nn), 500), random_state=0).astype(str).str.strip()
    looks_like_date = sample.str.contains(r"\d", regex=True) & sample.str.contains(
        r"[-/:]|\d\s+[A-Za-z]{3}|[A-Za-z]{3}\s+\d", regex=True
    )
    if looks_like_date.mean() < 0.9:
        return None
    if pd.to_numeric(sample, errors="coerce").notna().mean() > 0.5:
        return None

    from pandas.tseries.api import guess_datetime_format

    fmt = guess_datetime_format(sample.iloc[0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if fmt:
            parsed = pd.to_datetime(nn.astype(str).str.strip(), format=fmt, errors="coerce")
            if parsed.notna().mean() >= 0.95:
                return date_summary(parsed, fmt)
        if pd.to_datetime(sample, format="mixed", errors="coerce").notna().mean() >= 0.95:
            parsed = pd.to_datetime(nn.astype(str).str.strip(), format="mixed", errors="coerce")
            return date_summary(parsed, "mixed formats")
    return None


def date_summary(parsed: pd.Series, fmt: str) -> dict:
    ok = parsed.dropna()
    return {
        "format": fmt,
        "min": ok.min(),
        "max": ok.max(),
        "unparsed": int(parsed.isna().sum()),
        "distinct_days": int(ok.dt.normalize().nunique()),
        "has_time": bool((ok.dt.hour != 0).any() or (ok.dt.minute != 0).any()),
    }


def profile_column(name: str, s: pd.Series, n_rows: int) -> dict:
    nn = s.dropna()
    info: dict = {
        "name": name,
        "dtype": str(s.dtype),
        "kind": kind_of(s),
        "missing": int(s.isna().sum()),
        "unique": int(nn.nunique()),
        "flags": [],
    }
    vc = nn.value_counts()
    info["value_counts"] = vc
    info["examples"] = [md(show(v), 24) for v in vc.index[:3]]

    if nn.empty:
        info["flags"].append(("empty", "column is entirely empty"))
        return info
    if info["unique"] == 1:
        info["flags"].append(("constant", f"single value {md(vc.index[0])!r} in every non-missing row"))
    elif vc.iloc[0] / len(nn) >= DOMINANT_VALUE:
        info["flags"].append(("dominant", f"{md(vc.index[0])!r} in {pct(vc.iloc[0], len(nn))} of non-missing rows"))

    if info["missing"] / n_rows >= MOSTLY_MISSING:
        info["flags"].append(("mostly_missing", f"{pct(info['missing'], n_rows)} missing"))

    if info["unique"] == len(nn) and len(nn) == n_rows and info["kind"] in {"numeric", "text"}:
        info["flags"].append(("identifier", "unique in every row (row identifier?)"))

    if info["kind"] == "numeric":
        profile_numeric(nn, vc, info)
    elif info["kind"] == "text":
        profile_text(name, nn, vc, info)
    return info


def profile_numeric(nn: pd.Series, vc: pd.Series, info: dict) -> None:
    x = nn.astype("float64")
    q1, med, q3 = x.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    outliers = int(((x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)).sum()) if iqr > 0 else 0
    info["stats"] = {
        "min": x.min(), "q1": q1, "median": med, "mean": x.mean(), "q3": q3, "max": x.max(),
        "std": x.std(), "zeros": int((x == 0).sum()), "negatives": int((x < 0).sum()), "outliers": outliers,
    }
    if info["unique"] == 2 and set(vc.index.astype(float)) == {0.0, 1.0}:
        info["binary"] = True
    if outliers / len(x) >= OUTLIER_SHARE_FLAG:
        info["flags"].append(("outliers", f"{pct(outliers, len(x))} of values outside 1.5×IQR"))
    if pd.api.types.is_float_dtype(nn) and (x % 1 == 0).all() and info["missing"] > 0:
        info["flags"].append(("int_as_float", "whole numbers stored as float (because of missing values)"))
    top = vc.index[0]
    if float(top) in SENTINELS and vc.iloc[0] / len(nn) > 0.01:
        info["flags"].append(("sentinel", f"{num(top)} appears in {pct(vc.iloc[0], len(nn))} of rows (placeholder code?)"))


def profile_text(name: str, nn: pd.Series, vc: pd.Series, info: dict) -> None:
    sv = nn.astype(str)
    info["avg_len"] = float(sv.str.len().mean())

    placeholders = [(v, c) for v, c in vc.items() if PLACEHOLDER_RE.match(str(v))]
    if placeholders:
        desc = ", ".join(f"{md(v)!r} ×{c:,}" for v, c in placeholders[:4])
        info["flags"].append(("placeholder", f"placeholder/masked values: {desc}"))

    date_info = detect_datetime(nn)
    if date_info:
        info["date"] = date_info
        info["flags"].append(("date_as_text", f"dates stored as text (format `{date_info['format']}`)"))
        return

    numeric_share = pd.to_numeric(sv.str.strip(), errors="coerce").notna().mean()
    if numeric_share >= 0.95:
        info["flags"].append(("number_as_text", f"{numeric_share:.0%} of values are numbers stored as text"))
    else:
        cleaned = sv.str.replace(r"[,$€£%\s]", "", regex=True)
        if pd.to_numeric(cleaned, errors="coerce").notna().mean() >= 0.95:
            info["flags"].append(("formatted_number", "numbers with formatting characters ($, %, commas)"))

    padded = int((sv != sv.str.strip()).sum())
    if padded:
        info["flags"].append(("whitespace", f"{padded:,} values have leading/trailing whitespace"))

    if info["unique"] <= 50_000:
        uniques = pd.Series(vc.index.astype(str)).str.strip().drop_duplicates()
        norm = uniques.str.casefold()
        dup = uniques[norm.duplicated(keep=False)]
        if not dup.empty:
            groups = dup.groupby(norm[dup.index]).apply(list).head(3)
            examples = "; ".join(" / ".join(repr(md(v, 20)) for v in g) for g in groups)
            n_var = norm[dup.index].nunique()
            info["flags"].append(("case_variants", f"{n_var:,} value{'s' if n_var != 1 else ''} differ{'s' if n_var == 1 else ''} only by letter case, e.g. {examples}"))

    mojibake = int(sv.str.contains(MOJIBAKE_RE, regex=True).sum())
    if mojibake:
        info["flags"].append(("mojibake", f"{mojibake:,} values contain garbled characters (encoding problem)"))

    if info["avg_len"] > 50 and info["unique"] / len(nn) > 0.5:
        info["flags"].append(("free_text", f"free text (avg. {info['avg_len']:.0f} characters)"))


# --------------------------------------------------------------------------- table-level checks


def column_fingerprint(s: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
        s = s.astype("float64").round(6)
    else:
        s = s.astype(str)
    return hashlib.sha1(pd.util.hash_pandas_object(s, index=False).values.tobytes()).hexdigest()


def duplicate_columns(df: pd.DataFrame) -> list[list[str]]:
    groups: dict[str, list[str]] = {}
    for col in df.columns:
        if df[col].notna().any():
            groups.setdefault(column_fingerprint(df[col]), []).append(col)
    return [cols for cols in groups.values() if len(cols) > 1]


def one_to_one_columns(df: pd.DataFrame, profiles: dict, exclude: set[str]) -> list[tuple[str, str]]:
    """Pairs of columns that encode the same grouping (e.g. an ID and its name)."""
    by_unique: dict[int, list[str]] = {}
    for col, p in profiles.items():
        if col not in exclude and 2 < p["unique"] <= 5000 and p["missing"] == 0:
            by_unique.setdefault(p["unique"], []).append(col)
    pairs = []
    for cols in by_unique.values():
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                if df.groupby(a)[b].nunique().max() == 1:
                    pairs.append((a, b))
    return pairs


# --------------------------------------------------------------------------- report


FLAG_SECTIONS = [
    ("empty", "Empty columns"),
    ("constant", "Constant columns"),
    ("placeholder", "Placeholder or masked values"),
    ("mojibake", "Encoding problems"),
    ("mostly_missing", "Mostly missing (≥50%)"),
    ("date_as_text", "Dates stored as text"),
    ("number_as_text", "Numbers stored as text"),
    ("formatted_number", "Numbers with formatting"),
    ("whitespace", "Leading/trailing whitespace"),
    ("case_variants", "Inconsistent spelling/case"),
    ("dominant", "Nearly constant (one value ≥99%)"),
    ("sentinel", "Possible placeholder codes"),
    ("int_as_float", "Whole numbers stored as float"),
    ("outliers", "Many IQR outliers (≥5%)"),
    ("free_text", "Free-text columns"),
    ("identifier", "Row identifiers"),
]


def profile_file(path: Path, dictionary: dict[str, str]) -> tuple[str, dict]:
    df, encoding = read_table(path)
    n_rows, n_cols = df.shape
    profiles = {col: profile_column(col, df[col], n_rows) for col in df.columns}
    dup_rows = int(df.duplicated().sum())
    dup_cols = duplicate_columns(df)
    in_dup = {c for group in dup_cols for c in group[1:]}
    pairs = one_to_one_columns(df, profiles, in_dup)
    padded_names = [c for c in df.columns if c != c.strip()]

    out = [f"## {path.name}", ""]
    out += [
        f"- **Rows × columns:** {n_rows:,} × {n_cols}",
        f"- **Read with:** `{encoding}`" + ("  ← not UTF-8; pass `encoding=` to `pd.read_csv`" if encoding not in {"utf-8", "excel", "parquet", "json"} else ""),
        f"- **Memory in pandas:** {df.memory_usage(deep=True).sum() / 1e6:,.0f} MB",
        f"- **Fully duplicated rows:** {count_pct(dup_rows, n_rows) if dup_rows else 'none'}",
        f"- **Columns with missing values:** {sum(1 for p in profiles.values() if p['missing'])} of {n_cols}",
        "",
    ]

    # ---- flags
    out += ["### Flags", "", "_Things to check before cleaning. Each one may be fine; that's for you to decide._", ""]
    any_flag = False
    if padded_names:
        any_flag = True
        out.append(f"**Column names with leading/trailing spaces:** " + ", ".join(f"`{md(c, None)!r}`" for c in padded_names))
        out.append("")
    if dup_cols:
        any_flag = True
        out.append("**Identical columns** (same values in every row):")
        out += [f"- " + " = ".join(f"`{md(c, None)}`" for c in group) for group in dup_cols]
        out.append("")
    if pairs:
        any_flag = True
        out.append("**1:1 mappings** (each value of one column matches exactly one value of the other, e.g. an ID and its name):")
        out += [f"- `{md(a, None)}` ↔ `{md(b, None)}`" for a, b in pairs]
        out.append("")
    for key, title in FLAG_SECTIONS:
        hits = [(col, msg) for col, p in profiles.items() for k, msg in p["flags"] if k == key]
        if not hits:
            continue
        any_flag = True
        out.append(f"**{title}:**")
        out += [f"- `{md(col, None)}`: {msg}" for col, msg in hits]
        out.append("")
    if not any_flag:
        out += ["No flags.", ""]

    # ---- column table
    matched = sum(normalise_name(c) in dictionary for c in df.columns)
    has_dict = bool(dictionary) and matched / n_cols >= 0.3
    headers = ["#", "Column", "Type", "Missing", "Unique", "Most common values"] + (["Description"] if has_dict else [])
    rows = []
    for i, (col, p) in enumerate(profiles.items(), 1):
        kind = ("empty" if p["unique"] == 0 else "date (text)" if "date" in p
                else "binary 0/1" if p.get("binary") else p["kind"])
        row = [str(i), f"`{md(col, None)}`", f"{kind} ({p['dtype']})", count_pct(p["missing"], n_rows),
               num(p["unique"]), ", ".join(p["examples"])]
        if has_dict:
            row.append(md(dictionary.get(normalise_name(col), "—"), 70))
        rows.append(row)
    out += ["### Columns", "", table(headers, rows), ""]

    # ---- numeric
    numeric = {c: p for c, p in profiles.items() if "stats" in p and not p.get("binary")}
    if numeric:
        rows = []
        for col, p in numeric.items():
            st = p["stats"]
            n = n_rows - p["missing"]
            rows.append([f"`{md(col, None)}`", num(st["min"]), num(st["q1"]), num(st["median"]), num(st["mean"]),
                         num(st["q3"]), num(st["max"]), num(st["std"]), pct(st["zeros"], n),
                         pct(st["negatives"], n), pct(st["outliers"], n)])
        out += ["### Numeric columns", "",
                table(["Column", "Min", "25%", "Median", "Mean", "75%", "Max", "Std", "Zeros", "Negative", "IQR outliers"], rows), ""]

    # ---- dates
    dates = {c: p["date"] for c, p in profiles.items() if "date" in p}
    native = {c: date_summary(df[c], "native datetime") for c, p in profiles.items() if p["kind"] == "datetime" and df[c].notna().any()}
    dates.update(native)
    if dates:
        rows = []
        for col, d in dates.items():
            f = "%Y-%m-%d %H:%M" if d["has_time"] else "%Y-%m-%d"
            rows.append([f"`{md(col, None)}`", f"`{d['format']}`", d["min"].strftime(f), d["max"].strftime(f),
                         num((d["max"] - d["min"]).days), num(d["distinct_days"]), num(d["unparsed"])])
        out += ["### Date/time columns", "",
                table(["Column", "Format", "Earliest", "Latest", "Span (days)", "Distinct days", "Unparsed"], rows), ""]

    # ---- distributions
    low = {c: p for c, p in profiles.items() if 1 < p["unique"] <= LOW_CARDINALITY}
    if low:
        out += ["### Value distributions (columns with ≤25 distinct values)", ""]
        for col, p in low.items():
            vc, total = p["value_counts"], n_rows
            parts = [f"{md(show(v), 30)} {pct(c, total)}" for v, c in vc.head(TOP_N).items()]
            if len(vc) > TOP_N:
                parts.append(f"… +{len(vc) - TOP_N} more")
            if p["missing"]:
                parts.append(f"*missing* {pct(p['missing'], total)}")
            out.append(f"- **`{md(col, None)}`** ({p['unique']}): " + " · ".join(parts))
        out.append("")

    # ---- dictionary coverage
    if has_dict:
        cols_norm = {normalise_name(c): c for c in df.columns}
        undocumented = [c for n, c in cols_norm.items() if n not in dictionary]
        unmatched = [k for k in dictionary if k not in cols_norm]
        out += ["### Data dictionary coverage", "",
                f"- Columns without a description: " + (", ".join(f"`{md(c, None)}`" for c in undocumented) or "none"),
                f"- Dictionary entries with no matching column: " + (", ".join(f"`{k}`" for k in unmatched) or "none"),
                ""]

    summary = {"file": path, "rows": n_rows, "cols": n_cols, "encoding": encoding,
               "size_mb": path.stat().st_size / 1e6,
               "flags": sum(len(p["flags"]) for p in profiles.values()) + len(dup_cols) + len(pairs) + bool(padded_names)}
    return "\n".join(out), summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="data files to profile (default: everything in data/raw/)")
    parser.add_argument("--dictionary", type=Path, help="data dictionary file (field name, description)")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "data-profile.md")
    args = parser.parse_args()

    files = [f.resolve() for f in args.files] or discover_files(ROOT / "data" / "raw")
    dict_files = [args.dictionary.resolve()] if args.dictionary else [f for f in files if is_dictionary_file(f)]
    data_files = [f for f in files if f not in dict_files]
    if not data_files:
        print("No data files found. Download the data into data/raw/ first.", file=sys.stderr)
        return 1

    dictionary: dict[str, str] = {}
    for f in dict_files:
        dictionary.update(load_dictionary(f))

    sections, summaries = [], []
    for f in data_files:
        print(f"Profiling {f.name} …", file=sys.stderr)
        try:
            text, summary = profile_file(f, dictionary)
        except ImportError as exc:
            print(f"  skipped: {exc}", file=sys.stderr)
            continue
        sections.append(text)
        summaries.append(summary)

    def rel(p: Path) -> str:
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)

    header = [
        "# Data Profile", "",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M} by `scripts/profile-data.py`. "
        "Re-run the script to regenerate this file, and don't edit it by hand._", "",
        "This file lists facts about the raw data and flags things to check. "
        "It doesn't interpret them; the decisions belong in the data-preparation notebook.", "",
        table(["File", "Rows", "Columns", "Size", "Encoding", "Flags"],
              [[f"[{s['file'].name}](#{re.sub(r'[^a-z0-9-]', '', s['file'].name.lower())})", f"{s['rows']:,}",
                str(s["cols"]), f"{s['size_mb']:,.1f} MB", f"`{s['encoding']}`", str(s["flags"])] for s in summaries]),
        "",
    ]
    if dict_files:
        header += ["Data dictionary: " + ", ".join(f"`{rel(f)}`" for f in dict_files) + f" ({len(dictionary)} entries)", ""]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(header + sections).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {rel(args.output.resolve())}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
