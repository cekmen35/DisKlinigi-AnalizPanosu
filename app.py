import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

# --- 1) Veri Hazırlama ---

def load_data(path: str) -> pd.DataFrame:
    try:
        frame = pd.read_csv(path)
    except FileNotFoundError:
        raise SystemExit("HATA: 'veri.csv' bulunamadı. Klasörde olduğundan emin olun.")

    if 'Tarih' in frame.columns:
        frame['Tarih'] = pd.to_datetime(frame['Tarih'], errors='coerce')
    return frame


df = load_data('veri.csv')

# Tür listeleri
hizmet_turleri = sorted([h for h in df['Hizmet_Turu'].dropna().unique()]) if 'Hizmet_Turu' in df else []
kaynaklar = sorted([k for k in df['Kaynak'].dropna().unique()]) if 'Kaynak' in df else []

min_tarih = pd.to_datetime(df['Tarih'].min()) if 'Tarih' in df else None
max_tarih = pd.to_datetime(df['Tarih'].max()) if 'Tarih' in df else None


# --- 2) Uygulama ---

app = dash.Dash(__name__)
app.title = 'Veri Analiz Panosu'


# --- 3) Arayüz ---

controls = html.Div(
    style={
        'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)', 'marginBottom': '16px'
    },
    children=[
        html.Div([
            html.Div([
                html.Label('Tarih Aralığı'),
                dcc.DatePickerRange(
                    id='date-range',
                    display_format='YYYY-MM-DD',
                    start_date=min_tarih if min_tarih is not None else None,
                    end_date=max_tarih if max_tarih is not None else None,
                )
            ], style={'flex': 1, 'minWidth': '220px', 'marginRight': '12px'}),
            html.Div([
                html.Label('Hizmet Türü'),
                dcc.Dropdown(
                    id='hizmet-filter',
                    options=[{'label': h, 'value': h} for h in hizmet_turleri],
                    multi=True,
                    placeholder='Seçiniz'
                )
            ], style={'flex': 1, 'minWidth': '220px', 'marginRight': '12px'}),
            html.Div([
                html.Label('Kaynak'),
                dcc.Dropdown(
                    id='kaynak-filter',
                    options=[{'label': k, 'value': k} for k in kaynaklar],
                    multi=True,
                    placeholder='Seçiniz'
                )
            ], style={'flex': 1, 'minWidth': '220px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap'}),

        html.Div([
            html.Button('Filtreleri Uygula', id='apply-filters', n_clicks=0, style={'marginRight': '8px'}),
            dcc.Download(id='download-data'),
            html.Button('Filtreli Veriyi İndir (CSV)', id='download-btn', n_clicks=0)
        ], style={'marginTop': '12px'})
    ]
)


def kpi_card(title: str, value: str) -> html.Div:
    return html.Div(
        style={
            'backgroundColor': 'white', 'padding': '16px', 'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.06)', 'flex': 1, 'minWidth': '180px'
        },
        children=[
            html.Div(title, style={'color': '#666', 'fontSize': '13px', 'marginBottom': '6px'}),
            html.Div(value, style={'fontSize': '22px', 'fontWeight': 'bold'})
        ]
    )


app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4', 'padding': '20px'},
    children=[
        html.H1('Diş Kliniği Veri Analiz Panosu', style={'textAlign': 'center', 'color': '#333'}),
        html.Div('Gelen ön kayıtların interaktif analizi.', style={'textAlign': 'center', 'color': '#555', 'marginBottom': '24px'}),

        controls,

        html.Div(id='kpi-row', style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '16px'}),

        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px'},
            children=[
                html.Div([dcc.Graph(id='hizmet-bar')]),
                html.Div([dcc.Graph(id='kaynak-pie')]),
                html.Div([dcc.Graph(id='trend-line')]),
                html.Div([dcc.Graph(id='yas-hist')])
            ]
        ),

        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px', 'marginTop': '16px'},
            children=[
                html.Div([
                    html.H3('Tanımlayıcı İstatistikler', style={'margin': 0, 'marginBottom': '8px'}),
                    html.Div(id='desc-stats', style={'backgroundColor': 'white', 'padding': '12px', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.06)'}),
                ]),
                html.Div([
                    html.H3('Korelasyon (Sayısal Değişkenler)', style={'margin': 0, 'marginBottom': '8px'}),
                    dcc.Graph(id='corr-heatmap')
                ])
            ]
        )
    ]
)


# --- 4) Yardımcılar ---

def filter_dataframe(data: pd.DataFrame, start_date, end_date, hizmetler, kaynaklar_list) -> pd.DataFrame:
    result = data.copy()
    if 'Tarih' in result and start_date is not None and end_date is not None:
        result = result[(result['Tarih'] >= pd.to_datetime(start_date)) & (result['Tarih'] <= pd.to_datetime(end_date))]
    if 'Hizmet_Turu' in result and hizmetler:
        result = result[result['Hizmet_Turu'].isin(hizmetler)]
    if 'Kaynak' in result and kaynaklar_list:
        result = result[result['Kaynak'].isin(kaynaklar_list)]
    return result


def make_desc_stats(data: pd.DataFrame) -> html.Table:
    numeric_cols = data.select_dtypes(include=[np.number])
    if numeric_cols.empty:
        return html.Table([html.Tr([html.Td('Sayısal sütun bulunamadı')])])
    desc = numeric_cols.describe().T
    header = html.Tr([html.Th('Değişken')] + [html.Th(c) for c in desc.columns])
    rows = [html.Tr([html.Td(idx)] + [html.Td(f"{val:.2f}") for val in row]) for idx, row in desc.iterrows()]
    return html.Table([header] + rows, style={'width': '100%', 'borderCollapse': 'collapse'})


# --- 5) Callback'ler ---

@app.callback(
    Output('kpi-row', 'children'),
    Output('hizmet-bar', 'figure'),
    Output('kaynak-pie', 'figure'),
    Output('trend-line', 'figure'),
    Output('yas-hist', 'figure'),
    Output('desc-stats', 'children'),
    Output('corr-heatmap', 'figure'),
    Input('apply-filters', 'n_clicks'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('hizmet-filter', 'value'),
    State('kaynak-filter', 'value')
)
def update_dashboard(_, start_date, end_date, hizmet_filter, kaynak_filter):
    filtered = filter_dataframe(df, start_date, end_date, hizmet_filter, kaynak_filter)

    total_count = len(filtered)
    unique_services = filtered['Hizmet_Turu'].nunique() if 'Hizmet_Turu' in filtered else 0
    avg_age = filtered['Hasta_Yasi'].mean() if 'Hasta_Yasi' in filtered else np.nan

    kpis = [
        kpi_card('Toplam Kayıt', f"{total_count}"),
        kpi_card('Farklı Hizmet Sayısı', f"{unique_services}"),
        kpi_card('Ortalama Yaş', f"{avg_age:.1f}" if not np.isnan(avg_age) else '-')
    ]

    # Hizmet bar
    if 'Hizmet_Turu' in filtered and not filtered.empty:
        hizmet_counts = filtered['Hizmet_Turu'].value_counts().reset_index()
        hizmet_counts.columns = ['Hizmet Türü', 'Kayıt Sayısı']
        fig_bar = px.bar(hizmet_counts, x='Hizmet Türü', y='Kayıt Sayısı', title='Hizmet Türüne Göre Dağılım', color='Hizmet Türü')
    else:
        fig_bar = go.Figure()
        fig_bar.update_layout(title='Hizmet Türüne Göre Dağılım')

    # Kaynak pie
    if 'Kaynak' in filtered and not filtered.empty:
        kaynak_counts = filtered['Kaynak'].value_counts().reset_index()
        kaynak_counts.columns = ['Kaynak', 'Kayıt Sayısı']
        fig_pie = px.pie(kaynak_counts, names='Kaynak', values='Kayıt Sayısı', title='Kaynak Dağılımı', hole=0.3)
    else:
        fig_pie = go.Figure()
        fig_pie.update_layout(title='Kaynak Dağılımı')

    # Trend line
    if 'Tarih' in filtered and not filtered.empty:
        daily = filtered.groupby('Tarih').size().reset_index(name='Günlük Kayıt')
        fig_trend = px.line(daily, x='Tarih', y='Günlük Kayıt', title='Günlük Kayıt Trendi', markers=True)
    else:
        fig_trend = go.Figure()
        fig_trend.update_layout(title='Günlük Kayıt Trendi')

    # Yaş histogram
    if 'Hasta_Yasi' in filtered and not filtered['Hasta_Yasi'].dropna().empty:
        fig_hist = px.histogram(filtered, x='Hasta_Yasi', nbins=10, title='Hasta Yaşı Dağılımı')
    else:
        fig_hist = go.Figure()
        fig_hist.update_layout(title='Hasta Yaşı Dağılımı')

    # Tanımlayıcı istatistikler
    desc = make_desc_stats(filtered)

    # Korelasyon ısı haritası (sadece sayısal)
    numeric = filtered.select_dtypes(include=[np.number])
    if not numeric.empty and numeric.shape[1] >= 2:
        corr = numeric.corr(numeric_only=True)
        fig_corr = px.imshow(corr, text_auto=True, aspect='auto', title='Korelasyon Isı Haritası', color_continuous_scale='RdBu', zmin=-1, zmax=1)
    else:
        fig_corr = go.Figure()
        fig_corr.update_layout(title='Korelasyon Isı Haritası')

    return kpis, fig_bar, fig_pie, fig_trend, fig_hist, desc, fig_corr


@app.callback(
    Output('download-data', 'data'),
    Input('download-btn', 'n_clicks'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('hizmet-filter', 'value'),
    State('kaynak-filter', 'value'),
    prevent_initial_call=True
)
def download_filtered(n_clicks, start_date, end_date, hizmet_filter, kaynak_filter):
    filtered = filter_dataframe(df, start_date, end_date, hizmet_filter, kaynak_filter)
    return dcc.send_data_frame(filtered.to_csv, 'filtreli_veri.csv', index=False)


# --- 6) Sunucu ---
if __name__ == '__main__':
    app.run(debug=True)