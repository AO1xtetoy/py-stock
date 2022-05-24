from matplotlib import ticker
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('米国株価チャート')

# サイドバー表示エリア
st.sidebar.write("""
# GAFAM株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定してください。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 100, 50)

#メインコンテンツ
st.write(f"""
### 過去 **{days}日間** のGAFAM株価
""")

#データを取得(キャッシュに残す)
@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 3500.0, (0.0, 3500.0)
    )

    #ティッカー
    tickers = {
        'Apple':'AAPL',
        'Facebook':'FB',
        'Google':'GOOGL',
        'Amazon':'AMZN',
        'Microsoft':'MSFT'
    }

    df = get_data(days, tickers)
    companies = st.multiselect(
            '会社名を選択してください。',
            list(df.index),
            ['Google', 'Amazon', 'Facebook', 'Apple', 'Microsoft']
        )

    if not companies:
        st.error('少なくとも1社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value':'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "読み込み中..."
    )