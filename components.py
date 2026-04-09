import dash
from dash import dcc, html
import feffery_antd_components as fac


def get_random_generator_layout():
    return fac.AntdCard(
        title=html.Div(
            [
                html.Span("🎲 ", style={"marginRight": "8px"}),
                html.Span("随机数生成器"),
            ],
            style={"fontSize": "22px", "fontWeight": "bold", "color": "#1890ff"},
        ),
        style={
            "width": "600px",
            "margin": "50px auto",
            "boxShadow": "0 6px 16px rgba(0,0,0,0.08)",
            "borderRadius": "12px",
        },
        styles={
            "header": {"textAlign": "center", "borderBottom": "1px solid #f0f0f0"},
            "body": {"padding": "32px"},
        },
        children=[
            fac.AntdRow(
                gutter=20,
                children=[
                    # 最小值
                    fac.AntdCol(
                        span=12,
                        children=[
                            fac.AntdFormItem(
                                label="最小值 (Min)",
                                children=fac.AntdInputNumber(
                                    id="min-input",
                                    value=1,
                                    placeholder="输入最小值",
                                    style={"width": "100%"},
                                ),
                            )
                        ],
                    ),
                    # 最大值
                    fac.AntdCol(
                        span=12,
                        children=[
                            fac.AntdFormItem(
                                label="最大值 (Max)",
                                children=fac.AntdInputNumber(
                                    id="max-input",
                                    value=100,
                                    placeholder="输入最大值",
                                    style={"width": "100%"},
                                ),
                            )
                        ],
                    ),
                ],
            ),
            fac.AntdRow(
                gutter=20,
                children=[
                    # 小数位数
                    fac.AntdCol(
                        span=12,
                        children=[
                            fac.AntdFormItem(
                                label="小数点后位数",
                                children=fac.AntdInputNumber(
                                    id="decimal-input",
                                    value=0,
                                    min=0,
                                    max=10,
                                    placeholder="0-10",
                                    style={"width": "100%"},
                                ),
                            )
                        ],
                    ),
                    # 生成数量
                    fac.AntdCol(
                        span=12,
                        children=[
                            fac.AntdFormItem(
                                label="生成数量",
                                children=fac.AntdInputNumber(
                                    id="count-input",
                                    value=10,
                                    min=1,
                                    max=1000,
                                    placeholder="1-1000",
                                    style={"width": "100%"},
                                ),
                            )
                        ],
                    ),
                ],
            ),
            fac.AntdDivider(),
            fac.AntdRow(
                gutter=10,
                children=[
                    fac.AntdCol(
                        span=8,
                        children=[
                            fac.AntdButton(
                                "生成",
                                id="generate-btn",
                                type="primary",
                                size="large",
                                block=True,
                                style={"fontWeight": "bold"},
                            )
                        ],
                    ),
                    fac.AntdCol(
                        span=8,
                        children=[
                            fac.AntdButton(
                                "清空",
                                id="clear-btn",
                                type="default",
                                danger=True,
                                size="large",
                                block=True,
                                style={"fontWeight": "bold"},
                            )
                        ],
                    ),
                    fac.AntdCol(
                        span=8,
                        children=[
                            fac.AntdButton(
                                "复制",
                                id="copy-btn",
                                type="dashed",
                                size="large",
                                block=True,
                                style={"fontWeight": "bold"},
                            ),
                            dcc.Store(id="clipboard-dummy"),  # 用于辅助客户端复制回调
                        ],
                    ),
                ],
                style={"marginBottom": "24px"},
            ),
            html.Div(
                [
                    fac.AntdText(" 生成结果", strong=True, style={"fontSize": "16px"}),
                    fac.AntdText("（每行一个，可直接复制）", type="secondary"),
                ],
                style={
                    "marginBottom": "8px",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                },
            ),
            fac.AntdInput(
                id="result-output",
                mode="text-area",
                autoSize={"minRows": 8, "maxRows": 15},
                placeholder="结果将显示在这里...",
                readOnly=True,
                style={
                    "marginTop": "12px",
                    "backgroundColor": "#fcfcfc",
                    "fontFamily": "monospace",
                    "fontSize": "16px",
                },
            ),
            html.Div(
                id="copy-hint",
                style={
                    "textAlign": "center",
                    "marginTop": "16px",
                    "minHeight": "22px",
                },
            ),
        ],
    )


def get_deduplicator_layout():
    return fac.AntdCard(
        title=html.Div(
            [
                html.Span("🧹 ", style={"marginRight": "8px"}),
                html.Span("数据去重工具"),
            ],
            style={"fontSize": "22px", "fontWeight": "bold", "color": "#1890ff"},
        ),
        style={
            "width": "800px",
            "margin": "50px auto",
            "boxShadow": "0 6px 16px rgba(0,0,0,0.08)",
            "borderRadius": "12px",
        },
        styles={
            "header": {"textAlign": "center", "borderBottom": "1px solid #f0f0f0"},
            "body": {"padding": "32px"},
        },
        children=[
            dcc.Upload(
                id="upload-data",
                children=html.Div(["拖拽文件到这里或者 ", html.A("点击选择文件")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                accept=".xlsx, .xls, .csv, .txt",
                # Allow multiple files to be uploaded
                multiple=False,
            ),
            html.Div(
                "支持格式: .xlsx, .csv, .txt (Tab分隔)",
                style={"textAlign": "center", "color": "#999", "fontSize": "12px"},
            ),
            html.Div(id="output-data-upload"),
            fac.AntdDivider(),
            fac.AntdButton(
                "去重并下载",
                id="deduplicate-btn",
                type="primary",
                size="large",
                disabled=True,
                block=True,
            ),
            html.Div(
                id="deduplication-stats",
                style={"marginTop": "15px", "textAlign": "center", "fontSize": "16px"},
            ),
            html.Div(id="removed-data-preview", style={"marginTop": "24px"}),
            dcc.Download(id="download-dataframe-xlsx"),
            dcc.Store(id="stored-data"),
        ],
    )
