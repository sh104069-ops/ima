import streamlit as st

st.set_page_config(
    page_title="通信トラブル解決クエスト",
    page_icon="🛰️",
    layout="centered",
)

# ------------------------------------------------------------------
# スタイル
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .big-title {
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 0.2em;
    }
    .scene-box {
        background-color: #f2f4f8;
        border-left: 6px solid #35507a;
        padding: 1em 1.2em;
        border-radius: 8px;
        margin-bottom: 1em;
        line-height: 1.75;
    }
    .monster-box {
        background-color: #22203a;
        color: #f5f5f5;
        border-left: 6px solid #8a5cf6;
        padding: 1em 1.2em;
        border-radius: 8px;
        margin-bottom: 1em;
        line-height: 1.75;
    }
    .item-box {
        background-color: #fffaf0;
        border: 1px solid #e0c68a;
        border-radius: 8px;
        padding: 0.8em 1em;
        margin-bottom: 0.8em;
    }
    .clear-badge {
        display:inline-block;
        background-color:#e8fbe8;
        color:#1a7a1a;
        border:1px solid #1a7a1a;
        border-radius:16px;
        padding:2px 12px;
        margin:2px;
        font-size: 14px;
    }
    .locked-badge {
        display:inline-block;
        background-color:#f0f0f0;
        color:#999999;
        border:1px solid #cccccc;
        border-radius:16px;
        padding:2px 12px;
        margin:2px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# データ定義：探偵編
# 各ステージで「手がかり（観察事項）」を複数提示し、怪しいものを選ばせる。
# 加えて根拠を記述させ、単純な一問一答にしない。
# ------------------------------------------------------------------
DETECTIVE_STAGES = [
    {
        "no": "①",
        "title": "ハード面の問題",
        "scene": (
            "情報の授業中、教室の数台のパソコンが突然インターネットに接続できなくなった。"
            "現場を確認したところ、以下のような状況が見られた。"
        ),
        "clues": [
            "LANケーブルのコネクタ部分が、奥まで刺さっていないように見える",
            "ハブ（集線装置）の電源ランプが消灯している",
            "デスクトップの壁紙が、いつもと違う画像になっている",
            "ブラウザのブックマークの数がいつもより増えている",
            "ノートパソコンのWi-FiスイッチがOFFの位置になっている",
        ],
        "correct": {0, 1, 4},
        "prompt": "この中から、通信トラブルの原因として怪しいと考えられるものをすべて選びなさい。",
        "reasoning_prompt": "選んだ理由（なぜそれが怪しいと考えたか）を書きなさい。",
        "explain": (
            "通信トラブルの調査は、まず「近い場所」＝ハード（物理的な部分）の確認から始めるのが基本である。"
            "ケーブルの挿し込み、電源やランプの状態、Wi-Fiのスイッチなど、目視・手動で確認できる項目を優先的に洗い出す。"
            "壁紙やブックマークの変化は通信障害とは直接関係がない。"
        ),
    },
    {
        "no": "②",
        "title": "ソフト面の問題",
        "scene": (
            "ハード面を確認したが異常は見つからなかった。パソコンの状態を調べるため、"
            "コマンドプロンプトでいくつかの情報を確認した。"
        ),
        "clues": [
            "ipconfig の結果、IPアドレスが「169.254.x.x」と表示された",
            "タスクマネージャーでCPU使用率が10%だった",
            "ipconfig の結果、サブネットマスクが「255.255.255.0」と正常に表示された",
            "デフォルトゲートウェイの欄が空欄になっている",
            "ディスプレイの解像度が変更されている",
        ],
        "correct": {0, 3},
        "prompt": "この中から、IPアドレス取得に問題があると考えられる項目をすべて選びなさい。",
        "reasoning_prompt": "「169.254.x.x」という表示や、ゲートウェイが空欄であることが何を意味するか説明しなさい。",
        "explain": (
            "「169.254.x.x」は、DHCPサーバーからIPアドレスを取得できなかった端末に自動で割り振られる"
            "アドレス（APIPA）であり、正常にネットワークへ参加できていないサインである。"
            "デフォルトゲートウェイが空欄であることも、正しい設定が行われていない可能性を示す。"
        ),
    },
    {
        "no": "③",
        "title": "LAN環境の問題",
        "scene": (
            "IPアドレスの設定自体は正常だった生徒のパソコンについて、さらに調査を進める。"
            "デフォルトゲートウェイ（ルーター）に対して ping コマンドを実行した。"
        ),
        "clues": [
            "ping の結果、「応答時間 1ms」など複数回の応答が返ってきた",
            "ping の結果、「宛先ホストに到達できません」と表示された",
            "ping の結果、「要求がタイムアウトしました」が続けて表示された",
            "ブラウザの起動に3秒かかった",
            "キーボードの反応がわずかに遅い",
        ],
        "correct": {1, 2},
        "prompt": "この中から、LAN内（ルーターまでの区間）に問題があると判断できる結果をすべて選びなさい。",
        "reasoning_prompt": "ping の応答結果から、どこまで通信が届いていて、どこから先が届いていないと考えられるか説明しなさい。",
        "explain": (
            "デフォルトゲートウェイへの ping が失敗する場合、自分の端末からLANの出口（ルーター）"
            "までの区間に問題がある可能性が高い。正常な応答（応答時間が表示される状態）と比較して"
            "判断することが重要である。"
        ),
    },
    {
        "no": "④",
        "title": "インターネット境界の問題",
        "scene": (
            "別の生徒のパソコンでは、ルーターへの ping は成功した。次に、外部のIPアドレス"
            "（8.8.8.8 など）に対して ping を実行し、結果を比較した。"
        ),
        "clues": [
            "8.8.8.8 への ping で応答が返ってきた",
            "8.8.8.8 への ping がすべてタイムアウトした",
            "同じ時間帯に、他の教室のパソコンも外部サイトに接続できないと報告があった",
            "ノートパソコンのバッテリー残量が20%だった",
            "USBメモリが正しく認識されている",
        ],
        "correct": {1, 2},
        "prompt": "この中から、インターネットとの境界（学校の外側）に問題があると考えられる根拠をすべて選びなさい。",
        "reasoning_prompt": "「他の教室でも同様の症状が出ている」という情報は、原因の切り分けにどう役立つか説明しなさい。",
        "explain": (
            "ルーターまでは届くのに外部IPへの ping が失敗する場合、学校とインターネットの境界"
            "（回線やプロバイダ側）に問題がある可能性が高い。複数の教室で同時に同じ症状が"
            "出ている場合は、個々の端末ではなく、より上流の設備に原因があると推測できる。"
        ),
    },
    {
        "no": "⑤",
        "title": "名前解決とサービスの問題",
        "scene": (
            "8.8.8.8 への ping は成功するのに、ブラウザで www.example.co.jp を開こうとすると"
            "「このサイトにアクセスできません」と表示される生徒がいた。"
        ),
        "clues": [
            "8.8.8.8 への ping は正常に応答が返ってくる",
            "www.example.co.jp への ping が名前解決エラーで失敗する",
            "別のブラウザで同じサイトを開いても同じエラーが出る",
            "壁紙の色が薄い",
            "特定の1サイトだけがどのブラウザでも開けず、他のサイトは問題なく見られる",
        ],
        "correct": {1, 2, 4},
        "prompt": "この中から、DNS（名前解決）またはサイト側の問題を疑う根拠として適切なものをすべて選びなさい。",
        "reasoning_prompt": (
            "「数字（IPアドレス）では通信できるがサイト名では失敗する」ことと、"
            "「特定の1サイトだけが開けない」ことは、それぞれ何が原因だと考えられるか、分けて説明しなさい。"
        ),
        "explain": (
            "数字のIPアドレスへの通信が成功するのに、名前（URL）を使った通信だけが失敗する場合は、"
            "URLをIPアドレスに変換する「DNS」に問題があると考えられる。一方、特定のサイトだけが"
            "どの端末・ブラウザからも開けない場合は、DNSではなく相手サーバー側の障害である可能性が高い。"
        ),
    },
]

STAGE6_QUESTIONS = [
    "地震や台風などで地域全体の通信設備（基地局・回線）が損傷した場合、①〜⑤で行ったような"
    "切り分け（ケーブル確認、ipconfig、pingなど）は有効だと思うか。理由とともに述べなさい。",
    "大規模な通信障害が起きたとき、学校や地域社会にはどのような影響が考えられるか、"
    "できるだけ具体的に挙げなさい。",
    "通信が使えない状況を想定して、平常時から準備しておくべきことを一つ提案しなさい。",
]

# ------------------------------------------------------------------
# データ定義：RPG編
# 各階層で、複数のアイテム（道具・コマンド）の中から必要なものを選んで装備し、
# 魔物に立ち向かう。正解は階層ごとに複数個、他の階層のアイテムがダミーとして混ざる。
# ------------------------------------------------------------------
ALL_ITEMS = {
    "cable_check": "LANケーブル差し込みチェッカー（ケーブルが根元まで刺さっているか確認する）",
    "lamp_check": "電源ランプ確認ミラー（ハブ・ルーターのランプ点灯状況を確認する）",
    "port_watch": "ポート点滅観察のめがね（ポートの異常な高速点滅を見抜く）",
    "cable_reconnect": "ケーブル抜き差しの剣（一本ずつ抜き差しして原因のケーブルを特定する）",
    "ipconfig_scroll": "ipconfig /all の巻物（自分のIPアドレスとゲートウェイを確認する）",
    "ping_wand": "pingの杖（近い順に相手へ呼びかけ、応答があるか確認する）",
    "netconn_bow": "Test-NetConnectionの弓（特定のポートが開いているか遠くから調べる）",
    "firewall_key": "ファイアウォール確認の鍵（閉じている通信の扉を見つけて開ける）",
    "dns_bell": "DNSの鈴（名前とIPアドレスの対応関係を鳴らして確かめる）",
    "browser_shield": "ブラウザ・OS更新の盾（古い機種やソフトの不具合から身を守る）",
    "server_crystal": "サーバー状況確認の水晶（相手サイトがダウンしていないか遠くから見通す）",
}

RPG_STAGES = [
    {
        "layer": "第1層",
        "name": "物理層（Physical Layer）",
        "story": (
            "通信のもっとも基礎となる「物理的な道」の階層。電線・無線・光ファイバーなど、"
            "実際にデータが通る『物』の世界を守っている。"
        ),
        "monster": (
            "🐍 断線のヘビ：ケーブルの不完全な挿入や断線によって通信を断ち切る。\n"
            "📡 電波を食らう電子レンジ：2.4GHz帯のWi-Fiに電波干渉を起こす。"
        ),
        "item_pool": ["cable_check", "lamp_check", "ipconfig_scroll", "ping_wand", "browser_shield"],
        "correct": {"cable_check", "lamp_check"},
    },
    {
        "layer": "第2層",
        "name": "データリンク層（Data Link Layer）",
        "story": "直接つながっている隣の機器同士（PCとハブなど）で、MACアドレスを目印にデータを届ける階層。",
        "monster": "🔁 無限増殖のループ：配線を輪のようにつないでしまい、ネットワーク全体をパニックに陥らせる。",
        "item_pool": ["port_watch", "cable_reconnect", "dns_bell", "netconn_bow", "firewall_key"],
        "correct": {"port_watch", "cable_reconnect"},
    },
    {
        "layer": "第3層",
        "name": "ネットワーク層（Network Layer）",
        "story": (
            "IPアドレスという「住所」をもとに、世界中の巨大な迷路（インターネット）を通り抜け、"
            "目的の場所まで荷物をリレーする階層。"
        ),
        "monster": (
            "🚪 開かずのゲートウェイ：出口（ルーター）の設定が正しくない。\n"
            "📦 住所不明の迷子パケット：IPアドレスの設定ミスや重複。"
        ),
        "item_pool": ["ipconfig_scroll", "ping_wand", "port_watch", "dns_bell", "cable_reconnect"],
        "correct": {"ipconfig_scroll", "ping_wand"},
    },
    {
        "layer": "第4層",
        "name": "トランスポート層（Transport Layer）",
        "story": (
            "データの送受信にミスがないかを確認し、通信の「信頼性」を保つ階層。"
            "TCPやUDP、アプリを識別する「ポート番号」を扱う。"
        ),
        "monster": "🚧 封鎖された裏門：特定のアプリだけが使うポート（扉）がファイアウォールなどで閉じられている。",
        "item_pool": ["netconn_bow", "firewall_key", "ipconfig_scroll", "browser_shield", "cable_check"],
        "correct": {"netconn_bow", "firewall_key"},
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
            "🥶 フリーズの呪い：ブラウザ自体の不具合や、古いOS・機種による処理能力不足。\n"
            "🏚️ 応答なきサーバー：相手のサイトそのものがダウンしている。"
        ),
        "item_pool": ["dns_bell", "browser_shield", "server_crystal", "ping_wand", "cable_check"],
        "correct": {"dns_bell", "browser_shield", "server_crystal"},
    },
]

# ------------------------------------------------------------------
# セッション状態
# ------------------------------------------------------------------
def init_state():
    ss = st.session_state
    ss.setdefault("mode", None)
    ss.setdefault("det_stage", 0)
    ss.setdefault("det_cleared", [False] * len(DETECTIVE_STAGES))
    ss.setdefault("det_stage6_done", False)
    ss.setdefault("det_stage6_answers", [""] * len(STAGE6_QUESTIONS))
    ss.setdefault("det_feedback", None)
    ss.setdefault("rpg_stage", 0)
    ss.setdefault("rpg_cleared", [False] * len(RPG_STAGES))
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
        "身近な場所から遠い場所へ、ハードからソフトへ。通信トラブルの原因を「探偵」として"
        "証拠から推理したり、「勇者」としてOSI参照モデルの各層に潜む問題に立ち向かったりしよう。"
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔍 探偵編")
        st.write("現場に残された手がかりの中から怪しいものを選び出し、根拠を記述して原因を推理する。")
        if st.button("探偵編をはじめる", use_container_width=True):
            st.session_state.mode = "detective"
            st.rerun()
    with col2:
        st.markdown("### ⚔️ RPG編")
        st.write("OSI参照モデルの7階層に潜む魔物に対し、正しい道具を装備してから立ち向かう。")
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

        st.write(f"**{stage['prompt']}**")
        selected = set()
        for i, clue in enumerate(stage["clues"]):
            key = f"det_clue_{stage_idx}_{i}"
            checked = st.checkbox(clue, key=key)
            if checked:
                selected.add(i)

        reasoning = st.text_area(stage["reasoning_prompt"], key=f"det_reason_{stage_idx}")

        if st.button("推理を確定する", key=f"det_submit_{stage_idx}"):
            if not selected:
                ss.det_feedback = ("warn", "手がかりを少なくとも1つ選んでから確定してね。")
            elif not reasoning.strip():
                ss.det_feedback = ("warn", "選んだ根拠も記述してから確定しよう。")
            elif selected == stage["correct"]:
                ss.det_cleared[stage_idx] = True
                ss.det_feedback = ("ok", stage["explain"])
            else:
                missed = stage["correct"] - selected
                wrong = selected - stage["correct"]
                msg = "推理はまだ完全ではない。"
                if wrong:
                    msg += f"　選んだ中に、通信トラブルとは直接関係のないものが{len(wrong)}件含まれている。"
                if missed:
                    msg += f"　見落としている手がかりが{len(missed)}件ある。"
                msg += "　現場をもう一度よく確認してみよう。"
                ss.det_feedback = ("ng", msg)

        if ss.det_feedback:
            kind, msg = ss.det_feedback
            if kind == "ok":
                st.success("解決！ " + msg)
                if reasoning.strip():
                    st.caption(f"あなたの記述：{reasoning}")
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
        st.subheader("ステージ⑥　大規模通信障害が起こったら")
        st.markdown(
            '<div class="scene-box">地震や台風などにより、地域全体の通信設備が損傷することがある。'
            "これまでのステージのような切り分けが通用しない規模の障害について、自分の考えをまとめよう。</div>",
            unsafe_allow_html=True,
        )
        answers = []
        for i, q in enumerate(STAGE6_QUESTIONS):
            ans = st.text_area(q, value=ss.det_stage6_answers[i], key=f"det_q6_{i}")
            answers.append(ans)

        if st.button("提出する"):
            if all(a.strip() for a in answers):
                ss.det_stage6_answers = answers
                ss.det_stage6_done = True
                st.rerun()
            else:
                st.warning("すべての設問に記述してから提出しよう。")

        if ss.det_stage6_done:
            st.success(
                "大規模な通信障害では、個々の端末の切り分けだけでは対処できない範囲の被害が生じる。"
                "緊急連絡・避難情報の伝達手段が失われることも大きな課題であり、"
                "ラジオや掲示、地域の連絡網など、通信インフラに依存しない代替手段を"
                "平常時から把握しておくことが重要である。"
            )
            st.info("探偵編、全ステージ解決。お疲れさま。")

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
        st.markdown(
            f'<div class="monster-box">👹 潜んでいる魔物<br><br>{stage["monster"]}</div>',
            unsafe_allow_html=True,
        )

        st.write("**戦いに出る前に、道具倉庫から必要なアイテムを装備しよう。**")
        st.caption("この階層の魔物に効くアイテムを、必要な数だけ選んでチェックを入れること。他の階層用のアイテムも紛れている。")

        equipped = set()
        for item_id in stage["item_pool"]:
            label = ALL_ITEMS[item_id]
            key = f"rpg_item_{stage_idx}_{item_id}"
            checked = st.checkbox(label, key=key)
            if checked:
                equipped.add(item_id)

        if st.button("装備してたたかう！", key=f"rpg_submit_{stage_idx}"):
            if not equipped:
                ss.rpg_feedback = ("warn", "アイテムを1つ以上装備してから挑もう。")
            elif equipped == stage["correct"]:
                ss.rpg_cleared[stage_idx] = True
                ss.rpg_feedback = ("ok", None)
            else:
                missed = stage["correct"] - equipped
                wrong = equipped - stage["correct"]
                msg = "攻撃が決めきれず、魔物を取り逃してしまった。"
                if wrong:
                    msg += f"　装備の中に、この階層では効果のないアイテムが{len(wrong)}個ある。"
                if missed:
                    msg += f"　あと{len(missed)}個、必要な装備が足りていない。"
                msg += "　もう一度、道具倉庫を見直してみよう。"
                ss.rpg_feedback = ("ng", msg)

        if ss.rpg_feedback:
            kind, msg = ss.rpg_feedback
            if kind == "ok":
                st.success("魔物をたおした！")
                st.markdown(f'<div class="item-box">{stage_explain(stage)}</div>', unsafe_allow_html=True)
                if st.button("次の階層へ →"):
                    ss.rpg_stage += 1
                    ss.rpg_feedback = None
                    st.rerun()
            elif kind == "ng":
                st.error(msg)
            else:
                st.warning(msg)
    else:
        st.success("すべての階層の魔物をたおした。通信トラブルに立ち向かう知識と装備が身についたはずだ。")

    st.write("")
    if st.button("⬅ ホームに戻る", key="rpg_home"):
        ss.mode = None
        st.rerun()


def stage_explain(stage):
    items_text = "、".join(ALL_ITEMS[i].split("（")[0] for i in sorted(stage["correct"]))
    return f"有効だった装備：{items_text}。この階層のトラブルには、これらの道具・コマンドが対応している。"


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