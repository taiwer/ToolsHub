import dash
from dash import (
    dcc,
    html,
    Input,
    Output,
    State,
    no_update,
    dash_table,
    callback_context,
)
import feffery_antd_components as fac
import random
import pandas as pd
import base64
import io
import components

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div(
    [
        fac.AntdConfigProvider(
            primaryColor="#1890ff",
        ),
        fac.AntdLayout(
            [
                fac.AntdSider(
                    width=200,
                    style={
                        "overflow": "auto",
                        "height": "100vh",
                        "position": "fixed",
                        "left": 0,
                    },
                    children=[
                        html.Div(
                            "Tools Hub",
                            style={
                                "height": "32px",
                                "margin": "16px",
                                "background": "rgba(255, 255, 255, 0.2)",
                                "color": "#fff",
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "lineHeight": "32px",
                                "borderRadius": "4px",
                            },
                        ),
                        fac.AntdMenu(
                            id="menu",
                            theme="dark",
                            mode="inline",
                            currentKey="random",
                            menuItems=[
                                {
                                    "component": "Item",
                                    "props": {
                                        "key": "random",
                                        "title": "随机数生成器",
                                        "icon": "antd-number",
                                    },
                                },
                                {
                                    "component": "Item",
                                    "props": {
                                        "key": "dedup",
                                        "title": "去重工具",
                                        "icon": "antd-filter",
                                    },
                                },
                            ],
                        ),
                    ],
                ),
                fac.AntdContent(
                    html.Div(
                        id="page-content",
                        style={
                            "padding": "24px",
                            "marginLeft": "200px",
                            "minHeight": "100vh",
                        },
                    )
                ),
            ]
        ),
    ]
)


@app.callback(Output("page-content", "children"), Input("menu", "currentKey"))
def render_content(key):
    if key == "dedup":
        return components.get_deduplicator_layout()
    return components.get_random_generator_layout()


# --- Random Generator Callbacks ---
@app.callback(
    [Output("result-output", "value"), Output("copy-hint", "children")],
    [
        Input("generate-btn", "nClicks"),
        Input("clear-btn", "nClicks"),
        Input("copy-btn", "nClicks"),
    ],
    [
        State("min-input", "value"),
        State("max-input", "value"),
        State("decimal-input", "value"),
        State("count-input", "value"),
    ],
    prevent_initial_call=True,
)
def generate_random_numbers(
    n_clicks_gen, n_clicks_clear, n_clicks_copy, min_val, max_val, decimals, count
):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "clear-btn":
        return "", ""

    if trigger_id == "copy-btn":
        return no_update, fac.AntdText("✅ 已复制到剪贴板", type="success")

    if trigger_id == "generate-btn":
        if min_val is None:
            min_val = 1
        if max_val is None:
            max_val = 100
        if count is None:
            count = 10
        if decimals is None:
            decimals = 0

        if min_val >= max_val:
            return "❌ 错误：最小值必须小于最大值", fac.AntdText(
                "生成失败：参数错误", type="danger"
            )

        numbers = []
        try:
            for _ in range(int(count)):
                if decimals == 0:
                    num = random.randint(int(min_val), int(max_val))
                    numbers.append(str(num))
                else:
                    num = random.uniform(float(min_val), float(max_val))
                    numbers.append(f"{num:.{int(decimals)}f}")

            result = "\n".join(numbers)
            hint_text = fac.AntdText(
                f"✅ 成功生成 {count} 个随机数，范围 [{min_val}, {max_val}]",
                type="success",
            )
            return result, hint_text

        except Exception as e:
            return f"发生错误: {str(e)}", fac.AntdText("生成出错", type="danger")

    return no_update


# --- Deduplication Callbacks ---
def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        filename_lower = filename.lower()
        if filename_lower.endswith(".csv"):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename_lower.endswith(".xls") or filename_lower.endswith(".xlsx"):
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename_lower.endswith(".txt"):
            # Assume that the user uploaded a tab-separated text file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep="\t")
        else:
            return None
    except Exception as e:
        print(f"Error parsing file {filename}: {e}")
        return None
    return df


@app.callback(
    [
        Output("output-data-upload", "children"),
        Output("stored-data", "data"),
        Output("deduplicate-btn", "disabled"),
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def update_output(contents, filename):
    if contents is None:
        return no_update, no_update, True

    df = parse_contents(contents, filename)

    if df is not None:
        # Show first 5 rows
        # Check explicit columns requirement: "A列B列"
        # We will assume column 0 and 1.

        # Convert to records for table
        data_records = df.head(5).to_dict("records")
        columns = [{"name": i, "id": i} for i in df.columns]

        children = html.Div(
            [
                html.H5(f"文件名: {filename} (前5行预览)"),
                dash_table.DataTable(
                    data=data_records,
                    columns=columns,
                    style_table={"overflowX": "auto"},
                    page_size=5,
                ),
                html.Hr(),
            ]
        )
        # Store full dataframe in dcc.Store (as json)
        return children, df.to_json(date_format="iso", orient="split"), False
    else:
        return html.Div(["There was an error processing this file."]), None, True


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Output("deduplication-stats", "children"),
    Output("removed-data-preview", "children"),
    Input("deduplicate-btn", "nClicks"),
    State("stored-data", "data"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def deduplicate_and_download(n_clicks, json_data, filename):
    if json_data is None:
        return no_update, no_update, no_update

    # Use io.StringIO to ensure pandas reads it as a json string buffer, not a filename
    df = pd.read_json(io.StringIO(json_data), orient="split")

    # Requirement: "A列B列同时相同去重"
    # Logic: Deduplicate based on first and second columns if available, or just all columns if not specified?
    # User said "A列B列". In Excel, A and B are index 0 and 1.
    if len(df.columns) >= 2:
        subset = [df.columns[0], df.columns[1]]
    else:
        # Fallback to all columns if less than 2
        subset = None

    original_count = len(df)

    # Identify duplicated rows (keep='first' marks duplicates as True)
    duplicates_mask = df.duplicated(subset=subset, keep="first")
    df_removed = df[duplicates_mask]

    # Perform deduplication
    df_deduplicated = df.drop_duplicates(subset=subset, keep="first")
    dedup_count = len(df_deduplicated)
    removed_count = original_count - dedup_count

    if filename:
        name_part = filename.rsplit(".", 1)[0]
        new_filename = f"{name_part}_uni.xlsx"
    else:
        new_filename = "deduplicated_data_uni.xlsx"

    stats_msg = fac.AntdText(
        f"✅ 处理完成！原始数据: {original_count} 行 -> 去重后: {dedup_count} 行 (移除了 {removed_count} 行重复数据)",
        type="success",
        strong=True,
    )

    # Generate preview for removed rows if any
    removed_preview = None
    if removed_count > 0:
        # Get all rows that are part of duplicates (both kept and removed)
        all_dups_mask = df.duplicated(subset=subset, keep=False)
        df_all_dups = df[all_dups_mask].copy()

        # Add a status column: Kept (first occurrence) or Removed
        is_removed = df_all_dups.duplicated(subset=subset, keep="first")
        df_all_dups["处理状态"] = is_removed.apply(
            lambda x: "❌ 移除" if x else "✅ 保留"
        )

        # Sort by the deduplication keys to group them visually
        if subset:
            df_all_dups = df_all_dups.sort_values(by=subset)

        # Move 'Status' column to front
        cols = ["处理状态"] + [col for col in df_all_dups.columns if col != "处理状态"]
        df_all_dups = df_all_dups[cols]

        data_records = df_all_dups.head(20).to_dict(
            "records"
        )  # Preview first 20 related rows

        # Conditional formatting for the table
        style_data_conditional = [
            {
                "if": {"filter_query": '{处理状态} = "✅ 保留"'},
                "backgroundColor": "#f6ffed",
                "color": "#389e0d",
            },
            {
                "if": {"filter_query": '{处理状态} = "❌ 移除"'},
                "backgroundColor": "#fff1f0",
                "color": "#cf1322",
            },
        ]

        columns = [{"name": i, "id": i} for i in df_all_dups.columns]

        removed_preview = html.Div(
            [
                fac.AntdDivider(
                    "去重详情预览 (前20行涉及重复的数据)", lineColor="#1890ff"
                ),
                html.Div(
                    [
                        fac.AntdText(
                            "包含被保留的行(✅)和被删除的行(❌)，按内容分组显示。",
                            type="secondary",
                        ),
                    ],
                    style={"marginBottom": "10px"},
                ),
                dash_table.DataTable(
                    data=data_records,
                    columns=columns,
                    style_table={"overflowX": "auto"},
                    page_size=10,
                    style_header={"fontWeight": "bold", "textAlign": "left"},
                    style_cell={"textAlign": "left"},
                    style_data_conditional=style_data_conditional,
                ),
            ]
        )
    else:
        removed_preview = html.Div(
            [
                fac.AntdDivider("无重复数据", lineColor="#52c41a"),
                fac.AntdText("没有发现重复行。", type="secondary"),
            ]
        )

    return (
        dcc.send_data_frame(df_deduplicated.to_excel, new_filename, index=False),
        stats_msg,
        removed_preview,
    )


app.clientside_callback(
    """
    function(n_clicks, text) {
        if (!n_clicks || !text) {
            return window.dash_clientside.no_update;
        }

        const copyToClipboard = (str) => {
            const el = document.createElement('textarea');
            el.value = str;
            el.setAttribute('readonly', '');
            el.style.position = 'absolute';
            el.style.left = '-9999px';
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
        };

        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(
                function() {
                    // Success
                }, 
                function() {
                    // Fallback
                    copyToClipboard(text);
                }
            );
        } else {
            // Fallback for non-secure context
            copyToClipboard(text);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("clipboard-dummy", "data"),
    Input("copy-btn", "nClicks"),
    State("result-output", "value"),
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)

