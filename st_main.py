import streamlit as st
import glob
import pandas as pd
import logging

st.set_page_config(
    page_title="Visualize Grarph",
    # layout="wide",
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s,%(message)s")

graph_imgs = glob.glob('./graph_layout/*')


st.title('階層型グラフ表示')
df = pd.read_csv('./sprawlter_result2.csv')
# dfの表示
st.subheader("Sprawlterの算出結果")
st.dataframe(df.style.highlight_min(axis=0))

st.markdown('nnpens: nodeとnodeの重なり,　nepens: nodeとedgeの重なり,　eepens: edgeとedgeの重なり')
st.markdown('---')


st.subheader("パラメータ調整")
st.text('new_result = α × nnpen  +  β × nepen  +  γ × eepen')

with st.form("パラメータ"):
    get_param = st.columns(3)
    param_nnpen = get_param[0].number_input("nnpenの係数", min_value=0.0, max_value=1.0)
    param_nepen = get_param[1].number_input("nepenの係数", min_value=0.0, max_value=1.0)
    param_eepen = get_param[2].number_input("eepenの係数", min_value=0.0, max_value=1.0)

    # Submitボタン
    plot_button = st.form_submit_button('再計算する')
    if plot_button:
        new_df = df.copy()
        new_df.insert(4, 'new_result', param_nnpen * new_df.nnpens + param_nepen * new_df.nepens + param_eepen * new_df.eepens)
        st.dataframe(new_df.style.highlight_min(axis=0))
        # パラメータ値をログ出力
        logging.info('nn-ne-eeの係数,%s,%s,%s', param_nnpen, param_nepen, param_eepen)

# container
def draw_graph(key):
    input_txt = key + ': グラフ番号(0-199)'
    graph1 = st.number_input(input_txt, min_value=0, max_value=len(graph_imgs))
    if 0 <= graph1 < len(graph_imgs):
        graph_path = "./graph_layout/graph_" + str(graph1) + ".png"
        # グラフ番号をログ出力
        logging.info('グラフ描画,%s,%s', key, graph1)
        # グラフを表示
        st.image(graph_path)
    else:
        return st.error('0-99で入力')


# グラフの表示
st.subheader("グラフの比較表示")

# 上の段
upper_cols = st.columns(2)
for i in range(len(upper_cols)):
    with upper_cols[i]:
        draw_graph(str(i))

# 下の段
lower_cols = st.columns(2)
for i in range(len(lower_cols)):
    with lower_cols[i]:
        draw_graph(str(i+2))
        
# 大画面表示
st.markdown('---')
st.subheader("グラフの大画面表示")
draw_graph('big')