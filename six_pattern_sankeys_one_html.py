import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def hsl_palette(n: int, s=65, l=50):
    if n <= 0:
        return []
    return [f"hsl({int(360*i/n)}, {s}%, {l}%)" for i in range(n)]


def load_ops(xlsx_path: str) -> pd.DataFrame:
    xl = pd.ExcelFile(xlsx_path)
    df = xl.parse("Product portfolio")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    cols = [
        "Part number",
        "Serial number operation",
        "Machine routing",
        "Max transport batch size (pieces)",
        "Setup time (h)",
        "Process time (h)",
        "Idle time (h)",
    ]
    ops = df[cols].copy()
    ops["Part number"] = ops["Part number"].ffill()
    ops = ops.dropna(subset=["Machine routing"]).copy()

    ops["Serial number operation"] = pd.to_numeric(
        ops["Serial number operation"], errors="coerce")
    ops = ops.dropna(subset=["Serial number operation"]).sort_values(
        ["Part number", "Serial number operation"])

    ops["Machine routing"] = ops["Machine routing"].astype(str).str.strip()

    for c in ["Max transport batch size (pieces)", "Setup time (h)", "Process time (h)", "Idle time (h)"]:
        ops[c] = pd.to_numeric(ops[c], errors="coerce").fillna(0)

    ops["Max transport batch size (pieces)"] = ops["Max transport batch size (pieces)"].replace(
        0, 1)

    return ops


def load_demand(xlsx_path: str) -> pd.DataFrame:
    xl = pd.ExcelFile(xlsx_path)
    df = xl.parse("Order pattern")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    orders = df.rename(columns={"Number of parts": "Qty"}).copy()
    orders["Qty"] = pd.to_numeric(
        orders["Qty"], errors="coerce").fillna(0).astype(int)

    return orders.groupby("Part number", as_index=False)["Qty"].sum().rename(columns={"Qty": "Total demand (parts)"})


def build_part_sequences(ops: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    """Part -> machine sequence signature + demand."""
    part_seq = (
        ops.groupby("Part number")["Machine routing"]
        .apply(list)
        .reset_index(name="sequence")
    )
    part_seq["signature"] = part_seq["sequence"].apply(
        lambda seq: " -> ".join(seq))
    part_seq = part_seq.merge(demand, on="Part number", how="left").fillna(
        {"Total demand (parts)": 0})
    part_seq["Total demand (parts)"] = part_seq["Total demand (parts)"].astype(
        int)
    return part_seq


def top_k_patterns(part_seq: pd.DataFrame, k: int = 6) -> pd.DataFrame:
    """Return top-k routing patterns by summed demand."""
    pat = (
        part_seq.groupby("signature", as_index=False)
        .agg(total_demand=("Total demand (parts)", "sum"), n_parts=("Part number", "nunique"))
        .sort_values(["total_demand", "n_parts"], ascending=False)
        .head(k)
        .reset_index(drop=True)
    )
    pat["pattern_id"] = [f"R{i+1:02d}" for i in range(len(pat))]
    return pat


def build_transitions_with_time(ops: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    """
    Builds per-part per-transition link weights in HOURS:
    value_h = (process + idle + setup/batch) * demand
    """
    ops = ops.merge(demand, on="Part number", how="left").fillna(
        {"Total demand (parts)": 0})
    ops["Total demand (parts)"] = ops["Total demand (parts)"].astype(int)

    ops["time_per_piece_h"] = (
        ops["Process time (h)"] + ops["Idle time (h)"]
        + (ops["Setup time (h)"] /
           ops["Max transport batch size (pieces)"].astype(float))
    )

    ops["to_machine"] = ops.groupby("Part number")["Machine routing"].shift(-1)
    trans = ops.dropna(subset=["to_machine"]).copy()

    trans = trans.rename(
        columns={"Machine routing": "from", "to_machine": "to"})
    trans["value_h"] = trans["time_per_piece_h"] * \
        trans["Total demand (parts)"]

    return trans[["Part number", "from", "to", "value_h", "time_per_piece_h", "Total demand (parts)"]]


def make_pattern_sankey_data(part_seq: pd.DataFrame, trans: pd.DataFrame, signature: str):
    """Return nodes + link arrays for one pattern."""
    parts = set(part_seq.loc[part_seq["signature"] ==
                signature, "Part number"].astype(str))
    df = trans[trans["Part number"].astype(str).isin(parts)].copy()
    if df.empty:
        return None

    # nodes for this pattern
    nodes = sorted(set(df["from"]).union(set(df["to"])))
    node_index = {n: i for i, n in enumerate(nodes)}

    # color per part (inside this pattern)
    parts_sorted = sorted(df["Part number"].astype(str).unique())
    colors = hsl_palette(len(parts_sorted))
    part_color = dict(zip(parts_sorted, colors))

    sources = [node_index[x] for x in df["from"]]
    targets = [node_index[x] for x in df["to"]]
    values = df["value_h"].astype(float).tolist()
    link_colors = [part_color[str(p)] for p in df["Part number"].astype(str)]

    hover = (
        "Part: " + df["Part number"].astype(str)
        + "<br>" + df["from"].astype(str) + " → " + df["to"].astype(str)
        + "<br>Demand: " + df["Total demand (parts)"].astype(int).astype(str)
        + "<br>Time per piece (h): " +
        df["time_per_piece_h"].map(lambda x: f"{x:.4f}")
        + "<br>Total hours: " + df["value_h"].map(lambda x: f"{x:.2f}")
        + "<extra></extra>"
    )

    return dict(
        nodes=nodes,
        sources=sources,
        targets=targets,
        values=values,
        colors=link_colors,
        hover=hover,
    )


def build_one_html_with_6_sankeys(xlsx_path: str, out_html: str, grid_cols: int = 2):
    ops = load_ops(xlsx_path)
    demand = load_demand(xlsx_path)

    part_seq = build_part_sequences(ops, demand)
    patterns = top_k_patterns(part_seq, k=6)

    trans = build_transitions_with_time(ops, demand)

    # layout: 2x3 by default
    k = len(patterns)
    cols = max(1, int(grid_cols))
    rows = (k + cols - 1) // cols

    specs = [[{"type": "sankey"} for _ in range(cols)] for _ in range(rows)]
    subplot_titles = []

    for _, r in patterns.iterrows():
        subtitle = f"{r['pattern_id']} | demand={int(r['total_demand'])} | parts={int(r['n_parts'])}<br>{r['signature']}"
        subplot_titles.append(subtitle)

    # pad titles if last row not full
    while len(subplot_titles) < rows * cols:
        subplot_titles.append("")

    fig = make_subplots(rows=rows, cols=cols, specs=specs,
                        subplot_titles=subplot_titles)

    for idx, r in patterns.iterrows():
        pid = r["pattern_id"]
        sig = r["signature"]

        data = make_pattern_sankey_data(part_seq, trans, sig)
        if data is None:
            continue

        rr = idx // cols + 1
        cc = idx % cols + 1

        sankey = go.Sankey(
            arrangement="snap",
            node=dict(
                pad=18,
                thickness=16,
                line=dict(width=0.6),
                label=data["nodes"],
            ),
            link=dict(
                source=data["sources"],
                target=data["targets"],
                value=data["values"],
                color=data["colors"],
                hovertemplate=data["hover"],
            ),
        )

        fig.add_trace(sankey, row=rr, col=cc)

    fig.update_layout(
        title="Top 6 routing types — Sankey per routing (color=part, thickness=total hours)",
        font=dict(size=12),
        margin=dict(l=20, r=20, t=80, b=20),
        height=380 * rows,
    )

    fig.write_html(out_html, include_plotlyjs="cdn")
    print("Saved:", out_html)
    print(patterns[["pattern_id", "total_demand",
          "n_parts", "signature"]].to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Datasheet PSE 2026.xlsx")
    ap.add_argument("--out", default="Top6_Routing_Sankeys.html",
                    help="Output HTML file")
    ap.add_argument("--grid_cols", type=int, default=2,
                    help="Number of columns in the grid (default 2)")
    args = ap.parse_args()

    build_one_html_with_6_sankeys(
        args.xlsx, args.out, grid_cols=args.grid_cols)


if __name__ == "__main__":
    main()
