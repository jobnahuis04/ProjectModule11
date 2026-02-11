"""
Routing Pattern Miner for PSE dataset
- Reads Datasheet PSE 2026.xlsx
- Extracts each part's machine-routing sequence (ordered by operation number)
- Builds routing "patterns" and groups parts that share the same flow
- Optionally normalizes flows (remove immediate repeats, remove inspection, etc.)
- Optionally groups similar routings (edit-distance clustering)

Outputs:
- routing_library.csv: unique patterns + stats
- part_to_pattern.csv: each part assigned to a pattern
- routing_transitions.csv: From->To flows weighted by demand
"""

from __future__ import annotations

import re
import argparse
from dataclasses import dataclass
from typing import List, Dict, Tuple, Iterable, Optional

import pandas as pd


# -----------------------------
# Config / Normalization
# -----------------------------

@dataclass
class NormalizeConfig:
    strip_whitespace: bool = True
    uppercase: bool = True

    remove_immediate_repeats: bool = True
    # e.g., keep TM->...->TM? (usually keep)
    remove_self_loops_anywhere: bool = False
    drop_steps: Tuple[str, ...] = ()  # e.g. ("CMM",) to ignore inspection

    # Optional: map multiple codes to one family name (e.g. "TM1","TM2" -> "TM")
    map_codes: Dict[str, str] = None

    def __post_init__(self):
        if self.map_codes is None:
            self.map_codes = {}


def normalize_sequence(seq: List[str], cfg: NormalizeConfig) -> List[str]:
    """Normalize a routing sequence so identical flows match robustly."""
    out: List[str] = []
    prev: Optional[str] = None

    for s in seq:
        if cfg.strip_whitespace:
            s = str(s).strip()
        if cfg.uppercase:
            s = s.upper()

        # apply code mapping
        s = cfg.map_codes.get(s, s)

        # drop chosen steps
        if s in set(cfg.drop_steps):
            continue

        if cfg.remove_immediate_repeats and prev == s:
            continue

        out.append(s)
        prev = s

    if cfg.remove_self_loops_anywhere:
        # removes duplicates while preserving order (NOT recommended if revisits matter)
        seen = set()
        tmp = []
        for s in out:
            if s not in seen:
                tmp.append(s)
                seen.add(s)
        out = tmp

    return out


def seq_to_signature(seq: List[str]) -> str:
    return " -> ".join(seq)


# -----------------------------
# Similarity clustering (optional)
# -----------------------------

def levenshtein(a: List[str], b: List[str]) -> int:
    """Edit distance between token sequences."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n

    dp = list(range(m + 1))
    for i in range(1, n + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, m + 1):
            cur = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(
                dp[j] + 1,      # deletion
                dp[j - 1] + 1,  # insertion
                prev + cost     # substitution
            )
            prev = cur
    return dp[m]


def cluster_similar_patterns(
    patterns: pd.DataFrame,
    max_edit_distance: int = 1
) -> pd.DataFrame:
    """
    Greedy clustering of routing patterns by edit-distance.
    patterns must include columns: pattern_id, seq_tokens (list), total_demand
    Returns patterns with added cluster_id + cluster_rep (representative).
    """
    pats = patterns.sort_values("total_demand", ascending=False).copy()
    pats["cluster_id"] = None
    pats["cluster_rep"] = None

    cluster = 0
    reps: List[Tuple[int, List[str]]] = []  # (cluster_id, rep_tokens)

    for idx, row in pats.iterrows():
        tokens = row["seq_tokens"]
        assigned = False

        for cid, rep in reps:
            if levenshtein(tokens, rep) <= max_edit_distance:
                pats.at[idx, "cluster_id"] = cid
                pats.at[idx, "cluster_rep"] = seq_to_signature(rep)
                assigned = True
                break

        if not assigned:
            cluster += 1
            pats.at[idx, "cluster_id"] = cluster
            pats.at[idx, "cluster_rep"] = seq_to_signature(tokens)
            reps.append((cluster, tokens))

    return pats


# -----------------------------
# Core extraction
# -----------------------------

def load_ops_and_demand(xlsx_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    xl = pd.ExcelFile(xlsx_path)

    df_pp = xl.parse("Product portfolio")
    df_orders = xl.parse("Order pattern")

    df_pp.columns = [c.strip() if isinstance(
        c, str) else c for c in df_pp.columns]
    df_orders.columns = [c.strip() if isinstance(
        c, str) else c for c in df_orders.columns]

    # Operations table
    ops = df_pp[["Part number", "Serial number operation",
                 "Machine routing"]].copy()
    ops["Part number"] = ops["Part number"].ffill()
    ops = ops.dropna(subset=["Machine routing"]).copy()

    ops["Serial number operation"] = pd.to_numeric(
        ops["Serial number operation"], errors="coerce")
    ops = ops.dropna(subset=["Serial number operation"]).sort_values(
        ["Part number", "Serial number operation"])
    ops["Machine routing"] = ops["Machine routing"].astype(str)

    # Demand table
    orders = df_orders.rename(columns={"Number of parts": "Qty"}).copy()
    orders["Qty"] = pd.to_numeric(
        orders["Qty"], errors="coerce").fillna(0).astype(int)
    demand = orders.groupby("Part number", as_index=False)[
        "Qty"].sum().rename(columns={"Qty": "total_demand"})

    return ops, demand


def build_part_sequences(
    ops: pd.DataFrame,
    demand: pd.DataFrame,
    cfg: NormalizeConfig
) -> pd.DataFrame:
    # raw sequences
    part_seq = (
        ops.groupby("Part number")["Machine routing"]
        .apply(list)
        .reset_index(name="raw_sequence")
    )

    # normalize
    part_seq["sequence"] = part_seq["raw_sequence"].apply(
        lambda seq: normalize_sequence(seq, cfg))
    part_seq["signature"] = part_seq["sequence"].apply(seq_to_signature)

    # add demand
    part_seq = part_seq.merge(demand, on="Part number",
                              how="left").fillna({"total_demand": 0})
    part_seq["total_demand"] = part_seq["total_demand"].astype(int)

    return part_seq


def make_routing_library(part_seq: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    total = int(part_seq["total_demand"].sum()) or 1

    # pattern library
    lib = (
        part_seq.groupby("signature", as_index=False)
        .agg(
            n_parts=("Part number", "nunique"),
            total_demand=("total_demand", "sum"),
            example_parts=("Part number", lambda s: ", ".join(list(s.head(8))))
        )
        .sort_values(["total_demand", "n_parts"], ascending=False)
        .reset_index(drop=True)
    )

    lib["demand_share_pct"] = (lib["total_demand"] / total * 100).round(2)
    lib["pattern_id"] = [f"P{i+1:03d}" for i in range(len(lib))]

    # attach pattern_id to each part
    part_to_pattern = part_seq.merge(
        lib[["signature", "pattern_id"]], on="signature", how="left")

    # add token list to lib (useful for clustering)
    lib["seq_tokens"] = lib["signature"].apply(
        lambda s: s.split(" -> ") if isinstance(s, str) and s else [])

    return lib, part_to_pattern


def make_transition_table(part_seq: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in part_seq.iterrows():
        seq = r["sequence"]
        qty = int(r["total_demand"])
        for a, b in zip(seq, seq[1:]):
            rows.append((a, b, qty))

    trans = pd.DataFrame(rows, columns=["from", "to", "flow_parts"])
    if trans.empty:
        return trans
    return trans.groupby(["from", "to"], as_index=False)["flow_parts"].sum().sort_values("flow_parts", ascending=False)


# -----------------------------
# CLI
# -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True,
                    help="Path to Datasheet PSE 2026.xlsx")
    ap.add_argument("--out_prefix", default="routing_patterns",
                    help="Output file prefix")

    ap.add_argument("--drop_steps", default="",
                    help="Comma-separated steps to ignore (e.g., CMM,ET)")
    ap.add_argument("--no_immediate_repeat_removal",
                    action="store_true", help="Do NOT remove immediate repeats")
    ap.add_argument("--cluster", action="store_true",
                    help="Also cluster similar patterns")
    ap.add_argument("--max_edit_distance", type=int, default=1,
                    help="Edit distance threshold for clustering")

    args = ap.parse_args()

    cfg = NormalizeConfig(
        remove_immediate_repeats=not args.no_immediate_repeat_removal,
        drop_steps=tuple([s.strip().upper()
                         for s in args.drop_steps.split(",") if s.strip()])
    )

    ops, demand = load_ops_and_demand(args.xlsx)
    part_seq = build_part_sequences(ops, demand, cfg)
    lib, part_to_pattern = make_routing_library(part_seq)
    trans = make_transition_table(part_seq)

    # Save core outputs
    lib.drop(columns=["seq_tokens"]).to_csv(
        f"{args.out_prefix}_routing_library.csv", index=False)
    part_to_pattern.to_csv(
        f"{args.out_prefix}_part_to_pattern.csv", index=False)
    trans.to_csv(f"{args.out_prefix}_routing_transitions.csv", index=False)

    # Optional: cluster similar patterns
    if args.cluster:
        lib2 = cluster_similar_patterns(
            lib, max_edit_distance=args.max_edit_distance)
        lib2.drop(columns=["seq_tokens"]).to_csv(
            f"{args.out_prefix}_routing_library_clustered.csv", index=False)

    # Print quick summary
    print("=== Summary ===")
    print("Unique patterns:", len(lib))
    print("Top patterns by demand:")
    print(lib[["pattern_id", "total_demand", "demand_share_pct",
          "n_parts", "signature"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
