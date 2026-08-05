import streamlit as st

st.set_page_config(
    page_title="通信トラブル解決クエスト",
    page_icon="🛰️",
    layout="centered",
)

# ------------------------------------------------------------------
# スタイル（見やすさ重視：文字を大きめ・ボタンをはっきりと）
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-size: 18px;
    }
    div.stButton > button {
        font-size: 20px;
        padding: 0.6em 1.2em;
        border-radius: 12px;
        font-weight: bold;
    }
    div[data-testid="stRadio"] label {
        font-size: 19px;
    }
    .big-title {
        font-size: 34px;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .scene-box {
        background-color: #f0f4ff;
        border-left: 8px solid #4a6cf7;
        padding: 1em 1.2em;
        border-radius: 10px;
        margin-bottom: 1em;
        font-size: 19px;
        line-height: 1.7;
    }
    .monster-box {
        background-color: #2b2440;
        color: #ffffff;
        border-left: 8px solid #a259ff;
        padding: 1em 1.2em;
        border-radius: 10px;
        margin-bottom: 1em;
        font-size: 19px;
        line-height: 1.7;
    }
    .clear-badge {
        display:inline-block;
        background-color:#e8fbe8;
        color:#1a7a1a;
        border:2px solid #1a7a1a;
        border-radius:20px;
        padding:2px 14px;
        margin:2px;
        font-weight:bold;
    }
    .locked-badge {
        display:inline-block;
        background-color:#f0f0f0;
        color:#999999;
        border:2px solid #cccccc;
        border-radius:20px;
        padding:2px 14px;
        margin:2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# データ定義：探偵編（近い場所 → 遠い場所、ハード → ソフト）
# ------------------------------------------------------------------
DETECTIVE_STAGES = [
    {
        "no": "①",
        "title": "ハード面の問題",
        "scene": (
            "パソコンの画面に「インターネットに接続されていません」というマークが出ている。\n\n"
            "まず、いちばん最初に確認するべきことは何だろう？"
        ),
        "options": [
            "LANケーブルがきちんと差さっているか、電源やWi-FiのON/OFFを確認する",
            "パソコンのパスワードをすぐに変える",
            "ブラウザの拡張機能をすべて削除する",
            "デスクトップの壁紙を変えてみる",
        ],
        "answer": 0,
        "explain": (
            "通信トラブルの捜査は「近い場所」＝「ハード（物）」の確認からスタートするのが鉄則。"
            "ケーブルの抜け・電源・Wi-FiのON/OFFなど、目で見て手で確かめられることから調べよう。"
        ),
    },
    {
        "no": "②",
        "title": "ソフト面の問題",
        "scene": (
            "ケーブルも電源もWi-Fiも問題なかった。\n\n"
            "次に調べるべきことは何だろう？"
        ),
        "options": [
            "ipconfig コマンドで、自分のパソコンがIPアドレスをきちんと取得できているか確認する",
            "電源ボタンを何度も連打する",
            "先生に「直りません」とだけ伝えて終わる",
            "机の下のホコリを掃除する",
        ],
        "answer": 0,
        "explain": (
            "ハードに問題がなければ、次はソフト面。ipconfig でIPアドレスを確認し、"
            "きちんと住所（IPアドレス）をもらえているかをチェックする。"
        ),
    },
    {
        "no": "③",
        "title": "LAN環境の問題",
        "scene": (
            "ipconfig で確認すると、IPアドレスはちゃんと取得できていた。\n\n"
            "次はどこを調べる？"
        ),
        "options": [
            "デフォルトゲートウェイ（ルーター）に ping を送って、身近な出口まで届くか確認する",
            "いきなり学校のホームページを100回開いてみる",
            "教科書を最初から読み直す",
            "パソコンを窓の外に出してみる",
        ],
        "answer": 0,
        "explain": (
            "IPアドレスがあっても、家（教室）の外に出られなければ意味がない。"
            "まずは自分のいるLANの出口＝ルーター（デフォルトゲートウェイ）に ping を送って確かめよう。"
        ),
    },
    {
        "no": "④",
        "title": "インターネット境界の問題",
        "scene": (
            "ルーターへの ping はきちんと返ってきた。\n\n"
            "次に確かめることは？"
        ),
        "options": [
            "外部のIPアドレス（8.8.8.8など）に ping を送り、インターネットの外側まで届くか確認する",
            "諦めてパソコンを閉じる",
            "先生の分のパソコンだけ調べる",
            "USBメモリを何度も抜き差しする",
        ],
        "answer": 0,
        "explain": (
            "身近なルーターまでは届いた。次は、もっと遠く＝インターネットの外側（8.8.8.8など）"
            "まで届いているかを ping で確認する。"
        ),
    },
    {
        "no": "⑤",
        "title": "名前解決とサービスの問題",
        "scene": (
            "8.8.8.8 への ping は通った。でも、ブラウザで www.example.com を開こうとすると"
            "「サイトが見つかりません」と出てしまう。\n\n"
            "何が原因だろう？"
        ),
        "options": [
            "ドメイン名（サイトの名前）を数字のIPアドレスに変換する「DNS」がうまく働いていない",
            "パソコンの色がおかしい",
            "キーボードの配列が違う",
            "電源の差し込みが甘い",
        ],
        "answer": 0,
        "explain": (
            "数字（IPアドレス）では通信できるのに、名前（URL）ではダメなときは、"
            "名前をIPアドレスに変換する「DNS」のトラブルが疑われる。"
        ),
    },
]

STAGE6_QUESTIONS = [
    "大きな地震や台風などで、地域全体の通信設備（基地局やケーブル）が壊れてしまったら、どんなことが困ると思う？",
    "そのとき、スマホや学校のパソコンが使えなくても、連絡を取り合う方法は他にないだろうか？",
    "自分だったら、通信障害が起きた日に、まず何をする？",
]

# ------------------------------------------------------------------
# データ定義：RPG編（OSI参照モデル 7階層）
# ------------------------------------------------------------------
RPG_STAGES = [
    {
        "layer": "第1層",
        "name": "物理層（Physical Layer）",
        "story": (
            "通信のもっとも基礎となる「物理的な道」の階層。電線・無線・光ファイバーなど、"
            "実際にデータが通る『物』の世界を守っている。"
        ),
        "monster": (
            "🐍 カチッといわない断線のヘビ：ケーブルの不完全な挿入や断線で通信をさえぎる。\n"
            "📡 電波を食らう電子レンジ：2.4GHz帯のWi-Fiを妨害する電波干渉。"
        ),
        "question": "この階層の魔物をたおす『勇者の攻略法』はどれ？",
        "options": [
            "ハブやルーターの「POWERランプ」やケーブルの挿し込みを確認し、カチッというまで挿し直す",
            "呪文 ipconfig /all を唱える",
            "外部IP（8.8.8.8）に ping を放つ",
            "ブラウザを最新版に更新する",
        ],
        "answer": 0,
        "explain": (
            "物理層のトラブルは「目で見て・手で確かめる」のが基本。ランプの点灯やケーブルの挿し込みを確認しよう。"
        ),
    },
    {
        "layer": "第2層",
        "name": "データリンク層（Data Link Layer）",
        "story": (
            "直接つながっている隣の機器同士（PCとハブなど）で、MACアドレスを目印にデータを届ける階層。"
        ),
        "monster": (
            "🔁 無限増殖のループ：配線を輪のようにつないでしまい、ネットワークをパニックに陥らせる"
            "「ネットワークループ」が発生する。"
        ),
        "question": "この魔物をたおす『勇者の攻略法』はどれ？",
        "options": [
            "ハブの全ポートが同時に高速点滅していないか確認し、ケーブルを一本ずつ繋ぎ直して犯人を特定する",
            "デフォルトゲートウェイに ping を送る",
            "DNSサーバーの設定を確認する",
            "ブラウザのキャッシュを削除する",
        ],
        "answer": 0,
        "explain": (
            "全ポート高速点滅はループの合図。ケーブルを一度すべて抜き、一本ずつ挿し直して原因のケーブルを見つける。"
        ),
    },
    {
        "layer": "第3層",
        "name": "ネットワーク層（Network Layer）",
        "story": (
            "IPアドレスという「住所」をもとに、世界中の巨大な迷路（インターネット）を通り抜け、"
            "目的の場所まで荷物をリレーする階層。"
        ),
        "monster": (
            "🚪 開かずのゲートウェイ：出口（ルーター）が正しく設定されていない。\n"
            "📦 住所不明の迷子パケット：IPアドレスの設定ミスや重複。"
        ),
        "question": "この魔物をたおす『勇者の攻略法』はどれ？",
        "options": [
            "呪文 ipconfig /all で自分のIPアドレスとデフォルトゲートウェイを確認し、"
            "魔法 ping を「自分→出口（ルーター）→外の世界（8.8.8.8）」の順に放つ",
            "ハブのランプを見る",
            "ブラウザの拡張機能を消す",
            "パソコンを再起動せずに待つ",
        ],
        "answer": 0,
        "explain": (
            "ipconfig で住所を確認し、ping を近い順に放つことで、どこで通信が止まっているかを見極められる。"
        ),
    },
    {
        "layer": "第4層",
        "name": "トランスポート層（Transport Layer）",
        "story": (
            "データの送受信にミスがないかを確認し、通信の「信頼性」を保つ階層。"
            "TCPやUDP、アプリを識別する「ポート番号」を扱う。"
        ),
        "monster": "🚧 封鎖された裏門：特定のアプリだけが使うポート（扉）がファイアウォールなどで閉じられている。",
        "question": "この魔物をたおす『勇者の攻略法』はどれ？",
        "options": [
            "Test-NetConnection などの呪文で、特定のポート（扉）が開いているか調べる",
            "ケーブルを挿し直す",
            "電源を切って朝まで待つ",
            "教科書を音読する",
        ],
        "answer": 0,
        "explain": (
            "ping（第3層）は通るのに特定の通信だけ失敗する場合は、ポートが閉じている可能性がある。"
            "Test-NetConnection などで扉が開いているか確認しよう。"
        ),
    },
    {
        "layer": "第5〜7層",
        "name": "セッション・プレゼンテーション・アプリケーション層",
        "story": (
            "最上階は、私たちが実際に使うアプリや画面のルールを扱う階層。"
            "データの形式（文字コードや暗号化）や、ブラウザでの表示を管理する。"
        ),
        "monster": (
            "👻 名前を忘れた精霊（DNS）：URLをIPアドレスに変換できず、Webサイトが見つからない。\n"
            "🥶 フリーズの呪い：ブラウザ自体の不具合や、古いOS・機種による処理能力不足。"
        ),
        "question": "この魔物をたおす『勇者の攻略法』はどれ？",
        "options": [
            "数字（IPアドレス）での通信はできるのにサイト名での通信だけダメならDNSを疑い、"
            "特定のサイトだけ見られない場合は相手サーバーのダウンを疑い、"
            "ブラウザの更新や機種の見直しも検討する",
            "LANケーブルを交換する",
            "ハブの電源を切る",
            "デフォルトゲートウェイのIPアドレスを変更する",
        ],
        "answer": 0,
        "explain": (
            "数字（IP）は通るのに名前（URL）だけダメならDNSの問題。特定サイトだけダメなら相手サーバー側、"
            "全体的に重いならブラウザやOS・機種の見直しも検討しよう。"
        ),
    },
]

# ------------------------------------------------------------------
# セッション状態の初期化
# ------------------------------------------------------------------
def init_state():
    ss = st.session_state
    ss.setdefault("mode", None)
    ss.setdefault("det_stage", 0)
    ss.setdefault("det_cleared", [False] * len(DETECTIVE_STAGES))
    ss.setdefault("det_stage6_done", False)
    ss.setdefault("det_stage6_answers", ["", "", ""])
    ss.setdefault("rpg_stage", 0)
    ss.setdefault("rpg_cleared", [False] * len(RPG_STAGES))
    ss.setdefault("det_feedback", None)
    ss.setdefault("rpg_feedback", None)


init_state()


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


# ------------------------------------------------------------------
# ホーム画面
# ------------------------------------------------------------------
def show_home():
    st.markdown('<div class="big-title">🛰️ 通信トラブル解決クエスト</div>', unsafe_allow_html=True)
    st.write(
        "身近な場所から遠い場所へ、ハードからソフトへ。"
        "通信トラブルの原因を「探偵」のように見つけたり、"
        "「勇者」のようにOSI参照モデルの魔物をたおしたりしよう！"
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔍 探偵編")
        st.write("症状から原因を切り分けていく捜査パート。①〜⑥のステージがあるよ。")
        if st.button("探偵編をはじめる", use_container_width=True):
            st.session_state.mode = "detective"
            st.rerun()
    with col2:
        st.markdown("### ⚔️ RPG編")
        st.write("OSI参照モデルの7階層に潜む魔物を、正しい知識でたおしていこう。")
        if st.button("RPG編をはじめる", use_container_width=True):
            st.session_state.mode = "rpg"
            st.rerun()

    st.write("")
    st.divider()
    total_cleared = sum(st.session_state.det_cleared) + st.session_state.det_stage6_done + sum(
        st.session_state.rpg_cleared
    )
    total_all = len(DETECTIVE_STAGES) + 1 + len(RPG_STAGES)
    st.progress(total_cleared / total_all)
    st.caption(f"クリア状況：{total_cleared} / {total_all} ステージ")


# ------------------------------------------------------------------
# 探偵編
# ------------------------------------------------------------------
def show_detective():
    ss = st.session_state
    st.markdown('<div class="big-title">🔍 探偵編</div>', unsafe_allow_html=True)

    badges = ""
    for i, stage in enumerate(DETECTIVE_STAGES):
        cls = "clear-badge" if ss.det_cleared[i] else "locked-badge"
        badges += f'<span class="{cls}">{stage["no"]} {stage["title"]}</span> '
    cls6 = "clear-badge" if ss.det_stage6_done else "locked-badge"
    badges += f'<span class="{cls6}">⑥ 大規模通信障害</span>'
    st.markdown(badges, unsafe_allow_html=True)
    st.write("")

    stage_idx = ss.det_stage

    if stage_idx < len(DETECTIVE_STAGES):
        stage = DETECTIVE_STAGES[stage_idx]
        st.subheader(f"ステージ{stage['no']}　{stage['title']}")
        st.markdown(f'<div class="scene-box">{stage["scene"]}</div>', unsafe_allow_html=True)

        choice = st.radio(
            "原因だと思うものを選んでね",
            options=list(range(len(stage["options"]))),
            format_func=lambda i: stage["options"][i],
            key=f"det_radio_{stage_idx}",
            index=None,
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("けってい！", key=f"det_submit_{stage_idx}"):
                if choice is None:
                    ss.det_feedback = ("warn", "選択肢を選んでから「けってい！」を押してね。")
                elif choice == stage["answer"]:
                    ss.det_cleared[stage_idx] = True
                    ss.det_feedback = ("ok", stage["explain"])
                else:
                    ss.det_feedback = ("ng", "うーん、それは違うみたい。もう一度考えてみよう。")

        if ss.det_feedback:
            kind, msg = ss.det_feedback
            if kind == "ok":
                st.success("正解！🎉 " + msg)
                if st.button("次のステージへ →"):
                    ss.det_stage += 1
                    ss.det_feedback = None
                    st.rerun()
            elif kind == "ng":
                st.error(msg)
            else:
                st.warning(msg)
    else:
        # ステージ⑥ 大規模通信障害
        st.subheader("ステージ⑥　大規模通信障害が起こったら？")
        st.markdown(
            '<div class="scene-box">地震や台風などで、地域全体の通信設備がこわれてしまうこともある。'
            "そんなとき、どんな問題が起こると思う？　自分の考えを書いてみよう。</div>",
            unsafe_allow_html=True,
        )
        answers = []
        for i, q in enumerate(STAGE6_QUESTIONS):
            ans = st.text_area(q, value=ss.det_stage6_answers[i], key=f"det_q6_{i}")
            answers.append(ans)

        if st.button("書き終わった！"):
            ss.det_stage6_answers = answers
            ss.det_stage6_done = True
            st.rerun()

        if ss.det_stage6_done:
            st.success(
                "よく考えられたね！🎉 大規模な通信障害では、緊急連絡や避難情報を得る方法が失われることが"
                "大きな問題になる。ラジオ・張り紙・口頭での声かけなど、通信以外の連絡手段も知っておくと安心だね。"
            )
            st.balloons()
            st.info("探偵編、全ステージクリア！お疲れさま。")

    st.write("")
    if st.button("⬅ ホームに戻る"):
        ss.mode = None
        st.rerun()


# ------------------------------------------------------------------
# RPG編
# ------------------------------------------------------------------
def show_rpg():
    ss = st.session_state
    st.markdown('<div class="big-title">⚔️ RPG編：OSI参照モデルの魔物たち</div>', unsafe_allow_html=True)

    badges = ""
    for i, stage in enumerate(RPG_STAGES):
        cls = "clear-badge" if ss.rpg_cleared[i] else "locked-badge"
        badges += f'<span class="{cls}">{stage["layer"]}</span> '
    st.markdown(badges, unsafe_allow_html=True)
    st.write("")

    stage_idx = ss.rpg_stage

    if stage_idx < len(RPG_STAGES):
        stage = RPG_STAGES[stage_idx]
        st.subheader(f"{stage['layer']}　{stage['name']}")
        st.markdown(f'<div class="scene-box">{stage["story"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="monster-box">👹 潜んでいる魔物<br><br>{stage["monster"]}</div>', unsafe_allow_html=True)

        st.write(f"**{stage['question']}**")
        choice = st.radio(
            "攻略法を選んでね",
            options=list(range(len(stage["options"]))),
            format_func=lambda i: stage["options"][i],
            key=f"rpg_radio_{stage_idx}",
            index=None,
        )

        if st.button("たたかう！", key=f"rpg_submit_{stage_idx}"):
            if choice is None:
                ss.rpg_feedback = ("warn", "攻略法を選んでから「たたかう！」を押してね。")
            elif choice == stage["answer"]:
                ss.rpg_cleared[stage_idx] = True
                ss.rpg_feedback = ("ok", stage["explain"])
            else:
                ss.rpg_feedback = ("ng", "その攻撃は魔物に効かなかった…！もう一度考えよう。")

        if ss.rpg_feedback:
            kind, msg = ss.rpg_feedback
            if kind == "ok":
                st.success("魔物をたおした！🎉 " + msg)
                if st.button("次の階層へ →"):
                    ss.rpg_stage += 1
                    ss.rpg_feedback = None
                    st.rerun()
            elif kind == "ng":
                st.error(msg)
            else:
                st.warning(msg)
    else:
        st.success("すべての階層の魔物をたおした！🏆 通信の勇者になったね！")
        st.balloons()

    st.write("")
    if st.button("⬅ ホームに戻る", key="rpg_home"):
        ss.mode = None
        st.rerun()


# ------------------------------------------------------------------
# メイン
# ------------------------------------------------------------------
with st.sidebar:
    st.header("メニュー")
    if st.button("🏠 ホームへ"):
        st.session_state.mode = None
        st.rerun()
    st.divider()
    if st.button("🔄 進行状況をリセット"):
        reset_all()
        st.rerun()

if st.session_state.mode is None:
    show_home()
elif st.session_state.mode == "detective":
    show_detective()
elif st.session_state.mode == "rpg":
    show_rpg()