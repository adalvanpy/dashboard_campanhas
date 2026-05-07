import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def build_report_png(
    display_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    source: str,
    spent: float,
    impressions: float,
    leads: float,
    reach: float,
    cpl: float,
    cpc: float,
    brand_cyan: str,
    col_status: str | None,
    col_campaign: str | None,
) -> tuple[bytes, str]:
    export_bg = "#07133A"
    export_bg_deep = "#050B28"
    export_card = "#0C1F56"
    export_border = "#33C9EE"
    export_shadow_soft = "rgba(0, 0, 0, 0.12)"
    export_shadow_deep = "rgba(0, 0, 0, 0.07)"
    export_text = "#F3F8FF"

    report_fig = go.Figure()
    report_fig.update_layout(
        width=1080,
        height=1920,
        paper_bgcolor=export_bg,
        plot_bgcolor=export_bg,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(color=export_text, size=20),
    )

    report_fig.add_shape(
        type="rect",
        x0=0,
        x1=1,
        y0=0,
        y1=1,
        xref="paper",
        yref="paper",
        fillcolor=export_bg_deep,
        line_width=0,
        layer="below",
    )
    report_fig.add_shape(
        type="circle",
        x0=-0.1,
        x1=0.25,
        y0=0.72,
        y1=1.07,
        xref="paper",
        yref="paper",
        fillcolor="rgba(51, 201, 238, 0.13)",
        line_width=0,
        layer="below",
    )
    report_fig.add_shape(
        type="circle",
        x0=0.75,
        x1=1.18,
        y0=-0.08,
        y1=0.35,
        xref="paper",
        yref="paper",
        fillcolor="rgba(51, 201, 238, 0.10)",
        line_width=0,
        layer="below",
    )

    logo_file_export = Path("logob.png")
    logo_b64_export = None
    if logo_file_export.exists():
        logo_b64_export = base64.b64encode(logo_file_export.read_bytes()).decode("utf-8")

    if logo_b64_export:
        report_fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_b64_export}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.48,
                sizex=0.88,
                sizey=0.88,
                xanchor="center",
                yanchor="middle",
                opacity=0.12,
                layer="below",
            )
        )
        report_fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{logo_b64_export}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.055,
                sizex=0.24,
                sizey=0.24,
                xanchor="center",
                yanchor="bottom",
                opacity=1.0,
                layer="above",
            )
        )

    report_fig.add_shape(
        type="rect",
        x0=0,
        x1=1,
        y0=0.905,
        y1=1,
        xref="paper",
        yref="paper",
        fillcolor=export_bg_deep,
        line_width=0,
    )
    report_fig.add_shape(
        type="rect",
        x0=0,
        x1=0.02,
        y0=0.905,
        y1=1,
        xref="paper",
        yref="paper",
        fillcolor=brand_cyan,
        line_width=0,
    )

    report_fig.add_annotation(
        text="Relatório de Performance de Campanhas",
        x=0.53,
        y=0.975,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=50, color=export_text),
    )
    report_fig.add_annotation(
        text=f"Plataforma: {source}",
        x=0.53,
        y=0.94,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=30, color=export_border),
    )

    status_value = "—"
    if col_status and col_status in raw_df.columns and not raw_df[col_status].dropna().empty:
        status_value = str(raw_df[col_status].mode().iloc[0])

    campanha_value = "—"
    if col_campaign and col_campaign in raw_df.columns and not raw_df[col_campaign].dropna().empty:
        campanha_value = str(raw_df[col_campaign].dropna().iloc[0])[:30]

    kpi_cards = [
        ("Campanha", campanha_value),
        ("Status", status_value),
        ("Investido (R$)", f"R$ {spent:,.2f}"),
        ("Impressões", f"{impressions:,.0f}"),
        ("Contatos", f"{int(leads):,}"),
        ("Alcance", f"{reach:,.0f}"),
        ("CPL (R$)", f"R$ {cpl:,.2f}" if leads > 0 else f"R$ {cpc:,.2f}"),
    ]

    y_start = 0.855
    for i, (label_text, value_text) in enumerate(kpi_cards):
        y_val = y_start - i * 0.100
        title_x0 = 0.0
        title_x1 = 0.35
        value_x0 = 0.36
        value_x1 = 1.0

        report_fig.add_shape(
            type="rect",
            x0=title_x0 - 0.002,
            x1=value_x1 + 0.002,
            y0=y_val - 0.060,
            y1=y_val + 0.025,
            xref="paper",
            yref="paper",
            fillcolor="rgba(51, 201, 238, 0.14)",
            line_width=0,
        )
        report_fig.add_shape(
            type="rect",
            x0=title_x0 + 0.003,
            x1=title_x1 + 0.003,
            y0=y_val - 0.060,
            y1=y_val + 0.018,
            xref="paper",
            yref="paper",
            fillcolor=export_shadow_soft,
            line_width=0,
        )
        report_fig.add_shape(
            type="rect",
            x0=value_x0 + 0.003,
            x1=value_x1 + 0.003,
            y0=y_val - 0.060,
            y1=y_val + 0.018,
            xref="paper",
            yref="paper",
            fillcolor=export_shadow_deep,
            line_width=0,
        )
        report_fig.add_shape(
            type="rect",
            x0=title_x0,
            x1=title_x1,
            y0=y_val - 0.057,
            y1=y_val + 0.020,
            xref="paper",
            yref="paper",
            fillcolor=export_card,
            line_width=0,
        )
        report_fig.add_shape(
            type="rect",
            x0=value_x0,
            x1=value_x1,
            y0=y_val - 0.057,
            y1=y_val + 0.020,
            xref="paper",
            yref="paper",
            fillcolor=export_text,
            line_width=0,
        )
        report_fig.add_shape(
            type="rect",
            x0=title_x0,
            x1=title_x0 + 0.016,
            y0=y_val - 0.057,
            y1=y_val + 0.020,
            xref="paper",
            yref="paper",
            fillcolor=export_border,
            line_width=0,
        )
        report_fig.add_annotation(
            text=f"<b>{label_text}</b>",
            x=(title_x0 + title_x1) / 2,
            y=y_val - 0.018,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            font=dict(size=35, color=export_text),
        )
        report_fig.add_annotation(
            text=f"<b>{value_text}</b>",
            x=(value_x0 + value_x1) / 2,
            y=y_val - 0.018,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            font=dict(size=45, color=export_bg_deep),
        )

    png_9_16 = pio.to_image(
        report_fig,
        format="png",
        width=1080,
        height=1920,
        scale=2,
    )
    first_campaign = raw_df[col_campaign].dropna().iloc[0] if col_campaign and not raw_df[col_campaign].dropna().empty else "relatorio"
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in first_campaign).strip().replace(" ", "_")
    png_filename = f"{safe_name}_9x16.png"
    return png_9_16, png_filename