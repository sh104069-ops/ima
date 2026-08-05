
import base64
import io
import math
import struct
import wave

import streamlit as st
import streamlit.components.v1 as components

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
    .console-box {
        background-color: #10151c;
        color: #7CFC9A;
        font-family: "Consolas", "Courier New", monospace;
        border-radius: 8px;
        padding: 0.8em 1em;
        margin: 0.4em 0 1em 0;
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 15px;
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
    .explain-box {
        background-color: #fff8ea;
        border: 1px solid #e6c98a;
        border-radius: 8px;
        padding: 1em 1.2em;
        margin-top: 0.6em;
        line-height: 1.8;
    }
    .battle-log {
        background-color: #0e0e16;
        color: #e5e5e5;
        font-family: "Consolas", "Courier New", monospace;
        border-radius: 8px;
        padding: 0.8em 1em;
        margin-bottom: 0.8em;
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 15px;
        max-height: 260px;
        overflow-y: auto;
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
# BGM生成（外部音源を使わず、その場で簡易な音を合成する）
# ------------------------------------------------------------------
NOTE_FREQ = {
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00,
    "A3": 220.00, "Bb3": 233.08, "B3": 246.94,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00,
    "A4": 440.00, "Bb4": 466.16, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99,
    "A5": 880.00,
}


@st.cache_data(show_spinner=False)
def synth_bgm(notes, wave_type="square", volume=0.16, sample_rate=22050):
    """簡易チップチューン風のBGMをその場で合成し、WAV(base64)として返す。"""
    samples = []
    fade = max(1, int(sample_rate * 0.01))
    for note, dur in notes:
        freq = 0.0 if note is None else NOTE_FREQ[note]
        n = int(sample_rate * dur)
        for i in range(n):
            if freq == 0.0:
                s = 0.0
            else:
                t = i / sample_rate
                if wave_type == "square":
                    s = volume if math.sin(2 * math.pi * freq * t) >= 0 else -volume
                else:
                    s = volume * math.sin(2 * math.pi * freq * t)
                if i < fade:
                    s *= i / fade
                elif i > n - fade:
                    s *= (n - i) / fade
            samples.append(s)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            frames += struct.pack("<h", v)
        wf.writeframes(bytes(frames))
    return base64.b64encode(buf.getvalue()).decode("ascii")


# 探偵編：少し緊張感のある短調のフレーズ（ゆっくりめ）
DETECTIVE_NOTES = [
    ("D3", 0.35), ("F3", 0.35), ("G3", 0.35), ("F3", 0.35),
    ("D3", 0.35), (None, 0.2), ("A3", 0.35), ("D4", 0.7),
    ("C4", 0.35), ("Bb3", 0.35), ("A3", 0.35), ("F3", 0.35),
    ("G3", 0.35), (None, 0.2), ("D3", 0.9),
]

# RPG編：冒険感のある長調のフレーズ（テンポ良く）
RPG_NOTES = [
    ("C4", 0.18), ("E4", 0.18), ("G4", 0.18), ("C5", 0.18),
    ("G4", 0.18), ("E4", 0.18), ("C4", 0.18), (None, 0.1),
    ("D4", 0.18), ("F4", 0.18), ("A4", 0.18), ("D5", 0.18),
    ("A4", 0.18), ("F4", 0.18), ("D4", 0.18), (None, 0.1),
    ("E4", 0.18), ("G4", 0.18), ("C5", 0.18), ("E5", 0.36),
]

# ホーム画面：落ち着いたイントロ的フレーズ
HOME_NOTES = [
    ("C4", 0.5), ("E4", 0.5), ("G4", 0.5), ("C5", 1.0), (None, 0.5),
]


def render_bgm(mode):
    if mode == "detective":
        notes, wave_type = DETECTIVE_NOTES, "square"
    elif mode == "rpg":
        notes, wave_type = RPG_NOTES, "square"
    else:
        notes, wave_type = HOME_NOTES, "sine"
    track_b64 = synth_bgm(tuple(notes), wave_type=wave_type)
    html = f"""
    <audio autoplay loop>
      <source src="data:audio/wav;base64,{track_b64}" type="audio/wav">
    </audio>
    """
    components.html(html, height=0)


# ------------------------------------------------------------------
# データ定義：探偵編
# 各ステージで「調査アクション」を1つずつ実行（＝ボタンを押す）すると、
# 端末の出力のような結果が表示される。すべて調べたうえで、怪しい手がかりを
# 選び、根拠を記述する。単なる一覧提示ではなく「自分で調べに行く」体験にする。
# ------------------------------------------------------------------
DETECTIVE_STAGES = [
    {
        "no": "①",
        "title": "ハード面の問題",
        "scene": (
            "情報の授業中、教室の数台のパソコンが突然インターネットに接続できなくなった。"
            "あなたは現場に到着した探偵として、まず物理的な部分から調査を始める。"
            "気になる項目を選び、「調べる」ボタンを押して状況を確認していこう。"
        ),
        "clues": [
            {
                "action": "LANケーブルのコネクタを目視で確認する",
                "result": "コネクタのツメが浮いており、根元までしっかり刺さっていないことが分かった。",
                "suspicious": True,
            },
            {
                "action": "ハブ（集線装置）の電源ランプを確認する",
                "result": "本来点灯しているはずのPOWERランプが消えている。",
                "suspicious": True,
            },
            {
                "action": "デスクトップの壁紙を確認する",
                "result": "普段と違う画像に変わっているが、通信状態には影響しないはずだ。",
                "suspicious": False,
            },
            {
                "action": "ブラウザのブックマークを確認する",
                "result": "ブックマークの数が増えているが、通信状態とは無関係に見える。",
                "suspicious": False,
            },
            {
                "action": "ノートPCのWi-Fiスイッチの位置を確認する",
                "result": "本体側面のスイッチがOFFの位置に切り替わっていた。",
                "suspicious": True,
            },
        ],
        "prompt": "調査の結果から、通信トラブルの原因として怪しいと考えられるものをすべて選びなさい。",
        "reasoning_prompt": "選んだ理由（なぜそれが怪しいと考えたか）を書きなさい。",
        "explain": (
            "通信トラブルの調査は、身近な場所＝ハード（物理層）の確認から始めるのが定石である。"
            "LANケーブルは規格上、コネクタの「カチッ」という感触が出るまで奥に挿し込まないと"
            "接触不良を起こし、通信が不安定になったり完全に切断されたりする。"
            "また、ハブやルーターのPOWERランプが消えているのは、電源供給そのものが"
            "止まっている強いサインであり、装置全体が機能していない可能性を示す。"
            "Wi-FiスイッチのOFFも同様に、無線通信の入口が物理的に閉じられている状態であり、"
            "ソフトウェアの設定をいくら調べても解決しない。一方、壁紙やブックマークの変化は"
            "見た目上の違和感であっても、通信の仕組みには関与しないため、"
            "探偵としては「事件と無関係な情報」として除外する判断力も重要になる。"
        ),
        "keywords": ["ケーブル", "電源", "ランプ", "Wi-Fi", "無線", "スイッチ", "物理", "接続", "刺さ", "挿"],
    },
    {
        "no": "②",
        "title": "ソフト面の問題",
        "scene": (
            "ハード面を確認したが異常は見つからなかった。次はコマンドプロンプトを開き、"
            "端末の設定情報を1つずつ調べていく。"
        ),
        "clues": [
            {
                "action": "ipconfig を実行し、IPv4アドレスを確認する",
                "result": "IPv4アドレスが「169.254.35.12」と表示された。",
                "suspicious": True,
            },
            {
                "action": "タスクマネージャーでCPU使用率を確認する",
                "result": "CPU使用率はおよそ10%で、特に高負荷ではない。",
                "suspicious": False,
            },
            {
                "action": "ipconfig の結果でサブネットマスクを確認する",
                "result": "「255.255.255.0」と、通常想定される値が表示された。",
                "suspicious": False,
            },
            {
                "action": "ipconfig の結果でデフォルトゲートウェイを確認する",
                "result": "欄が空白のままで、何も表示されていない。",
                "suspicious": True,
            },
            {
                "action": "ディスプレイの解像度設定を確認する",
                "result": "設定は変更されておらず、通常通りだった。",
                "suspicious": False,
            },
        ],
        "prompt": "この中から、IPアドレスの取得に問題があると判断できる項目をすべて選びなさい。",
        "reasoning_prompt": "「169.254.x.x」という表示や、ゲートウェイが空欄であることが何を意味するか説明しなさい。",
        "explain": (
            "「169.254.x.x」という範囲のアドレスはAPIPA（Automatic Private IP Addressing）と呼ばれ、"
            "DHCPサーバーからIPアドレスを正しく取得できなかった端末に、Windowsなどが自動的に"
            "割り当てる特殊なアドレスである。人間に例えるなら「本来の住所（DHCPが配る住所）が"
            "もらえなかったので、とりあえず自分だけの仮の住所を名乗っている」状態であり、"
            "この状態のままではLANの外に出ることはできない。あわせてデフォルトゲートウェイの"
            "欄が空白であることも、出口となるルーターの情報が端末に伝わっていない証拠であり、"
            "根本的にはDHCPサーバー（多くの場合ルーター内蔵）との通信がうまくいっていないことを"
            "示している。サブネットマスクやCPU使用率、解像度設定は、この症状とは直接関係がない。"
        ),
        "keywords": ["IP", "アドレス", "169.254", "APIPA", "DHCP", "ゲートウェイ", "取得"],
    },
    {
        "no": "③",
        "title": "LAN環境の問題",
        "scene": (
            "IPアドレスの設定自体は正常だった別の生徒のパソコンについて、さらに調査を進める。"
            "コマンドプロンプトから、デフォルトゲートウェイ（ルーター）へ ping を送ってみよう。"
        ),
        "clues": [
            {
                "action": "デフォルトゲートウェイへ ping を実行する（1回目）",
                "result": "「要求がタイムアウトしました。」と表示された。",
                "suspicious": True,
            },
            {
                "action": "念のためもう一度、同じ相手へ ping を実行する",
                "result": "続けて「要求がタイムアウトしました。」と表示された。",
                "suspicious": True,
            },
            {
                "action": "隣の生徒のPCで同じ ping を試させてもらう",
                "result": "そのPCでは「応答時間 1ms」など、正常な応答が返ってきた。",
                "suspicious": False,
            },
            {
                "action": "ブラウザの起動時間を計測する",
                "result": "起動に3秒ほどかかったが、通信の問題とは考えにくい。",
                "suspicious": False,
            },
            {
                "action": "キーボードの反応を確認する",
                "result": "わずかに遅く感じるが、通信とは無関係と考えられる。",
                "suspicious": False,
            },
        ],
        "prompt": "この中から、LAN内（自分の端末からルーターまでの区間）に問題があると判断できる結果をすべて選びなさい。",
        "reasoning_prompt": "ping の応答結果から、通信はどこまで届いていて、どこから先が届いていないと考えられるか説明しなさい。",
        "explain": (
            "ping はICMPというプロトコルを使い、相手に「エコー要求」を送って「エコー応答」が"
            "返ってくるかを確認する、もっとも基本的な疎通確認コマンドである。デフォルトゲートウェイ"
            "（自分のLANの出口であるルーター）への ping が1回だけでなく繰り返し失敗している場合、"
            "たまたまの通信の揺らぎではなく、その端末からルーターまでの経路に継続的な問題が"
            "あると判断できる。一方、同じネットワーク内の別のPCからは正常に応答が返ってきていることから、"
            "ルーター自体や配線全体ではなく、その1台の端末に関わる部分（NIC、ケーブル、"
            "つながっているポートなど）に原因が絞り込める。このように「他の端末と比較する」ことは、"
            "問題を個体差なのか全体障害なのか切り分けるうえで欠かせない探偵の技術である。"
        ),
        "keywords": ["ping", "タイムアウト", "ゲートウェイ", "ルーター", "応答", "届", "経路"],
    },
    {
        "no": "④",
        "title": "インターネット境界の問題",
        "scene": (
            "別の生徒のパソコンでは、ルーターへの ping は成功した。今度は学校の外、"
            "つまりインターネットとの境界を調べてみよう。"
        ),
        "clues": [
            {
                "action": "外部IPアドレス 8.8.8.8 へ ping を実行する",
                "result": "「要求がタイムアウトしました。」が繰り返し表示された。",
                "suspicious": True,
            },
            {
                "action": "デフォルトゲートウェイへ ping を再確認する",
                "result": "「応答時間 1ms」など、正常な応答が返ってきた。",
                "suspicious": False,
            },
            {
                "action": "職員室に他の教室の状況を問い合わせる",
                "result": "複数の教室から、同じ時間帯に外部サイトへ接続できないとの報告があった。",
                "suspicious": True,
            },
            {
                "action": "ノートPCのバッテリー残量を確認する",
                "result": "残量は20%だった。通信状態には関係がない。",
                "suspicious": False,
            },
            {
                "action": "USBメモリの認識状況を確認する",
                "result": "正しく認識されており、特に問題は見られない。",
                "suspicious": False,
            },
        ],
        "prompt": "この中から、インターネットとの境界（学校の外側）に問題があると考えられる根拠をすべて選びなさい。",
        "reasoning_prompt": "「他の教室でも同様の症状が出ている」という情報は、原因の切り分けにどう役立つか説明しなさい。",
        "explain": (
            "ルーターまでの ping は成功しているため、LAN内部の疎通には問題がないことが分かる。"
            "その先の外部IPアドレス（8.8.8.8はGoogleが公開しているDNSサーバーで、疎通確認によく"
            "使われる）への ping が失敗している場合、学校とインターネットを結ぶ回線や、"
            "契約しているプロバイダ側の設備に問題がある可能性が高い。ここで重要な手がかりが"
            "「複数の教室で同時に同じ症状が出ている」という情報である。もし1台の端末だけの問題"
            "であれば、その端末のケーブルやNICを疑うべきだが、広い範囲で同時多発的に発生している"
            "場合は、個々の端末ではなく、より上流（学校全体が共有している回線や機器）に原因が"
            "あると推測できる。このように「影響範囲の広さ」を確認することは、ハード・ソフトの"
            "切り分けと並んで、原因を特定する上で非常に重要な視点である。"
        ),
        "keywords": ["外部", "8.8.8.8", "プロバイダ", "回線", "境界", "複数", "教室", "上流", "範囲"],
    },
    {
        "no": "⑤",
        "title": "名前解決とサービスの問題",
        "scene": (
            "8.8.8.8 への ping は成功するのに、ブラウザで www.example.co.jp を開こうとすると"
            "「このサイトにアクセスできません」と表示される生徒がいた。最後の調査に入ろう。"
        ),
        "clues": [
            {
                "action": "8.8.8.8 へ ping を実行する",
                "result": "正常に応答が返ってくる。",
                "suspicious": False,
            },
            {
                "action": "www.example.co.jp へ ping を実行する",
                "result": "「名前を解決できません」というエラーが表示され、IPアドレスに変換できなかった。",
                "suspicious": True,
            },
            {
                "action": "別のブラウザで同じサイトを開いてみる",
                "result": "別のブラウザでも同じアクセスエラーが表示された。",
                "suspicious": True,
            },
            {
                "action": "デスクトップの壁紙の色を確認する",
                "result": "特に変化は見られない。",
                "suspicious": False,
            },
            {
                "action": "他のWebサイトに複数アクセスできるか確認する",
                "result": "他のサイトはどれも問題なく開くことができた。",
                "suspicious": True,
            },
        ],
        "prompt": "この中から、DNS（名前解決）またはサイト側の問題を疑う根拠として適切なものをすべて選びなさい。",
        "reasoning_prompt": (
            "「数字（IPアドレス）では通信できるがサイト名では失敗する」ことと、"
            "「特定の1サイトだけが開けず、他のサイトは開ける」ことは、それぞれ何が原因だと考えられるか、分けて説明しなさい。"
        ),
        "explain": (
            "DNS（Domain Name System）は、人間が覚えやすい「ドメイン名（例：www.example.co.jp）」を、"
            "コンピュータが通信に使う「IPアドレス」に変換する仕組みである。8.8.8.8という数字への"
            "ping は成功するのに、ドメイン名への ping だけが名前解決エラーになる場合、"
            "ネットワークそのものは生きているが、名前をIPアドレスへ変換する機能（DNSサーバーへの"
            "問い合わせ）がうまく働いていないと判断できる。これはPC側のDNS設定の誤りや、"
            "学校が使っているDNSサーバーの不調が原因として考えられる。一方で、"
            "「特定の1サイトだけがどのブラウザでも開けず、他のサイトは正常」という場合は、"
            "自分たちのネットワークではなく、相手側のWebサーバーがダウンしている、"
            "あるいはメンテナンス中である可能性が高く、こちら側で対処できる範囲を超えている。"
            "このように症状の「範囲」（全サイトがダメなのか、特定の1サイトだけなのか）を"
            "見極めることが、DNSの問題と相手サーバーの問題を切り分ける決め手になる。"
        ),
        "keywords": ["DNS", "名前解決", "サーバー", "ドメイン", "IPアドレス", "変換"],
    },
]

STAGE6_QUESTIONS = [
    "地震や台風などで地域全体の通信設備（基地局・回線）が損傷した場合、①〜⑤で行ったような"
    "切り分け（ケーブル確認、ipconfig、pingなど）は有効だと思うか。理由とともに述べなさい。",
    "大規模な通信障害が起きたとき、学校や地域社会にはどのような影響が考えられるか、"
    "できるだけ具体的に挙げなさい。",
    "通信が使えない状況を想定して、平常時から準備しておくべきことを一つ提案しなさい。",
]

STAGE6_EXPLAIN = (
    "①〜⑤で行った切り分けは、あくまで「一部の端末や設備の不具合」を前提にした手法であり、"
    "基地局そのものや広域の回線が物理的に損壊するような大規模災害時には、そもそも調査対象の"
    "ネットワーク自体が丸ごと失われてしまうため、通用しないことが多い。実際の大規模通信障害では、"
    "音声通話の輻輳（同時に集中してつながりにくくなる現象）、SNSやメールなど個別サービスの"
    "障害、そして避難情報や安否確認手段の喪失といった問題が同時に発生する。"
    "そのため、学校や地域では、防災行政無線・ラジオ・紙の掲示・地域の連絡網など、"
    "通信インフラに依存しない代替の情報伝達手段をあらかじめ整えておくことが重要である。"
    "また、家族との集合場所を事前に決めておく、災害用伝言ダイヤル（171）の使い方を"
    "知っておくといった個人レベルの備えも、通信が使えない状況下では大きな意味を持つ。"
)

# ------------------------------------------------------------------
# データ定義：RPG編（ターン制バトル）
# 各階層で、正しいアイテムを選んで「攻撃」すると魔物にダメージが入り、
# 誤ったアイテムを使うと反撃を受けてしまう。すべての正解アイテムを
# 使い切ると魔物を倒せる、体験型のバトルにする。
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
        "explain": (
            "物理層は、ケーブルや電波など「モノ」として存在する通信経路を扱う、OSI参照モデルの"
            "最下層である。ここでの障害は目に見える形で現れることが多く、ソフトウェアの設定を"
            "いくら調べても解決しない点が特徴である。LANケーブル差し込みチェッカーで挿し込みを"
            "確認し、電源ランプ確認ミラーでハブやルーターへの通電状態を確認することが、"
            "もっとも基本的かつ確実な対処法となる。ipconfigやpingはこの層より上（ネットワーク層）"
            "のトラブルに使う道具であり、そもそも物理的な接続ができていない状態では実行しても"
            "無意味な結果しか得られない。"
        ),
    },
    {
        "layer": "第2層",
        "name": "データリンク層（Data Link Layer）",
        "story": "直接つながっている隣の機器同士（PCとハブなど）で、MACアドレスを目印にデータを届ける階層。",
        "monster": "🔁 無限増殖のループ：配線を輪のようにつないでしまい、ネットワーク全体をパニックに陥らせる。",
        "item_pool": ["port_watch", "cable_reconnect", "dns_bell", "netconn_bow", "firewall_key"],
        "correct": {"port_watch", "cable_reconnect"},
        "explain": (
            "データリンク層は、隣り合う機器同士がMACアドレスという固有の番号を頼りにデータを"
            "やり取りする層である。ここで起こりやすいのが「ネットワークループ」で、ケーブルを"
            "誤って輪のようにつないでしまうと、データが同じ経路をぐるぐると回り続け、"
            "ネットワーク全体の帯域を消費してしまう（ブロードキャストストームと呼ばれる現象）。"
            "ハブの全ポートが同時に激しく点滅している場合はループの合図であり、ポート点滅観察の"
            "めがねで異常を見抜き、ケーブルを一本ずつ抜き差しして原因のケーブルを特定するのが"
            "有効な対処法である。DNSやポート開放の道具はこの層より上位の問題に対応するものであり、"
            "ここでは効果を発揮しない。"
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
            "🚪 開かずのゲートウェイ：出口（ルーター）の設定が正しくない。\n"
            "📦 住所不明の迷子パケット：IPアドレスの設定ミスや重複。"
        ),
        "item_pool": ["ipconfig_scroll", "ping_wand", "port_watch", "dns_bell", "cable_reconnect"],
        "correct": {"ipconfig_scroll", "ping_wand"},
        "explain": (
            "ネットワーク層は、IPアドレスという「住所」を頼りに、複数のネットワークをまたいで"
            "データを目的地まで届ける役割を担う層である。ipconfig /allの巻物を使えば、自分の"
            "端末に割り当てられているIPアドレスやデフォルトゲートウェイの設定を確認でき、"
            "設定そのものに誤りがないかをまず見極めることができる。そのうえで、pingの杖を"
            "「自分→出口（ルーター）→外の世界（8.8.8.8など）」の順に近い相手から遠い相手へと"
            "段階的に使うことで、通信がどこまで届いていて、どこから先で止まっているのかを"
            "正確に切り分けられる。この『近い順に確認する』という考え方は、ネットワーク層の"
            "トラブルシューティングにおいて最も基本的な戦略である。"
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
        "item_pool": ["netconn_bow", "firewall_key", "ipconfig_scroll", "browser_shield", "cable_check"],
        "correct": {"netconn_bow", "firewall_key"},
        "explain": (
            "トランスポート層は、TCPやUDPといったプロトコルを使い、アプリケーションごとに"
            "「ポート番号」という扉を使い分けて通信の信頼性を確保する層である。ネットワーク層の"
            "ping（第3層）は正常に通るのに、特定のアプリやサービスだけがつながらない場合、"
            "そのアプリが使うポートがファイアウォールなどによって閉じられている可能性が高い。"
            "Test-NetConnectionの弓を使えば、対象のポート番号が開いているかどうかを遠くから"
            "確認でき、ファイアウォール確認の鍵を使えば、閉じている扉を見つけて設定を見直す"
            "ことができる。物理的な接続やIPアドレスの確認（ケーブルチェッカーやipconfig）は"
            "すでに問題なしと分かっている段階なので、ここでは効果を発揮しない。"
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
            "🥶 フリーズの呪い：ブラウザ自体の不具合や、古いOS・機種による処理能力不足。\n"
            "🏚️ 応答なきサーバー：相手のサイトそのものがダウンしている。"
        ),
        "item_pool": ["dns_bell", "browser_shield", "server_crystal", "ping_wand", "cable_check"],
        "correct": {"dns_bell", "browser_shield", "server_crystal"},
        "explain": (
            "セッション層・プレゼンテーション層・アプリケーション層は、私たちが日常的に触れる"
            "アプリやブラウザに近い、最も『上位』の層である。数字（IPアドレス）では通信できるのに"
            "サイト名では失敗する場合はDNSの鈴でドメイン名の解決状況を確認し、ブラウザやOSの"
            "不具合・古さが疑われる場合はブラウザ・OS更新の盾で対策する。また、特定の1サイトだけが"
            "誰から見ても開けない場合は、サーバー状況確認の水晶を使い、相手のサーバー自体が"
            "ダウンしていないかを確認する必要がある。この層のトラブルは原因が三者三様（自分の"
            "端末、通信経路、相手のサーバー）に分かれるため、より下位の層（第1〜4層）で"
            "問題がないことを確認したうえで、最後に切り分けるべき領域だと言える。"
        ),
    },
]

MONSTER_HP_PER_ITEM = 50
PLAYER_MAX_HP = 100
WRONG_ITEM_DAMAGE = 20

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
        "自分の手で調査し、「勇者」としてOSI参照モデルの各層に潜む魔物と実際に戦ってみよう。"
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔍 探偵編")
        st.write("現場で1つずつ調査を実行し、集まった手がかりから怪しいものを選んで根拠を記述する。")
        if st.button("探偵編をはじめる", use_container_width=True):
            st.session_state.mode = "detective"
            st.rerun()
    with col2:
        st.markdown("### ⚔️ RPG編")
        st.write("道具を選んで一手ずつ攻撃するターン制バトルで、OSI参照モデルの魔物に立ち向かう。")
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

        st.write("**気になる項目を選んで、実際に調べてみよう。**")

        revealed_key = f"det_revealed_{stage_idx}"
        ss.setdefault(revealed_key, set())
        judged_key = f"det_judged_{stage_idx}"
        ss.setdefault(judged_key, set())

        for i, clue in enumerate(stage["clues"]):
            with st.container():
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"手がかり{i + 1}：{clue['action']}")
                with cols[1]:
                    if i not in ss[revealed_key]:
                        if st.button("調べる", key=f"det_investigate_{stage_idx}_{i}"):
                            ss[revealed_key].add(i)
                            st.rerun()
                if i in ss[revealed_key]:
                    st.markdown(f'<div class="console-box">$ 調査結果 &gt; {clue["result"]}</div>', unsafe_allow_html=True)
                    checked = st.checkbox(
                        "この手がかりは怪しいと思う",
                        key=f"det_suspect_{stage_idx}_{i}",
                    )
                    if checked:
                        ss[judged_key].add(i)
                    else:
                        ss[judged_key].discard(i)

        st.write("")
        reasoning = st.text_area(stage["reasoning_prompt"], key=f"det_reason_{stage_idx}")

        if st.button("推理を確定する", key=f"det_submit_{stage_idx}"):
            if len(ss[revealed_key]) < len(stage["clues"]):
                ss.det_feedback = ("warn", "確定する前に、すべての手がかりを調べておこう。")
            elif not ss[judged_key]:
                ss.det_feedback = ("warn", "手がかりを少なくとも1つ「怪しい」と判断してから確定してね。")
            elif not reasoning.strip():
                ss.det_feedback = ("warn", "選んだ根拠も記述してから確定しよう。")
            else:
                correct = {i for i, c in enumerate(stage["clues"]) if c["suspicious"]}
                selection_ok = ss[judged_key] == correct
                keyword_ok = any(kw in reasoning for kw in stage.get("keywords", []))

                if selection_ok and keyword_ok:
                    ss.det_cleared[stage_idx] = True
                    ss.det_feedback = ("ok", stage["explain"])
                elif not selection_ok:
                    missed = correct - ss[judged_key]
                    wrong = ss[judged_key] - correct
                    msg = "推理はまだ完全ではない。"
                    if wrong:
                        msg += f"　選んだ中に、通信トラブルとは直接関係のないものが{len(wrong)}件含まれている。"
                    if missed:
                        msg += f"　見落としている手がかりが{len(missed)}件ある。"
                    msg += "　現場をもう一度よく確認してみよう。"
                    ss.det_feedback = ("ng", msg)
                else:
                    # 選択は正しいが、記述に関連語句が含まれていない
                    sample = "、".join(stage.get("keywords", [])[:4])
                    msg = (
                        "選んだ手がかりは正しいが、記述の中に関連する語句が見つからなかった。"
                        f"（例えば「{sample}」のような言葉を使って、根拠をもう少し具体的に書いてみよう。）"
                    )
                    ss.det_feedback = ("ng", msg)

        if ss.det_feedback:
            kind, msg = ss.det_feedback
            if kind == "ok":
                st.success("解決！")
                st.markdown(f'<div class="explain-box">{msg}</div>', unsafe_allow_html=True)
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
            st.success("提出完了。")
            st.markdown(f'<div class="explain-box">{STAGE6_EXPLAIN}</div>', unsafe_allow_html=True)
            st.info("探偵編、全ステージ解決。お疲れさま。")

    st.write("")
    if st.button("⬅ ホームに戻る"):
        ss.mode = None
        st.rerun()


# ------------------------------------------------------------------
# RPG編（ターン制バトル）
# ------------------------------------------------------------------
def get_combat_state(stage_idx, stage):
    ss = st.session_state
    key = f"rpg_combat_{stage_idx}"
    if key not in ss:
        ss[key] = {
            "monster_hp": len(stage["correct"]) * MONSTER_HP_PER_ITEM,
            "monster_max_hp": len(stage["correct"]) * MONSTER_HP_PER_ITEM,
            "player_hp": PLAYER_MAX_HP,
            "used_correct": set(),
            "log": [f"『{stage['name']}』の魔物が現れた！"],
            "result": None,  # None / "win" / "lose"
        }
    return ss[key]


def reset_combat(stage_idx, stage):
    key = f"rpg_combat_{stage_idx}"
    st.session_state.pop(key, None)
    get_combat_state(stage_idx, stage)


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
        combat = get_combat_state(stage_idx, stage)

        st.subheader(f"{stage['layer']}　{stage['name']}")
        st.markdown(f'<div class="scene-box">{stage["story"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="monster-box">👹 潜んでいる魔物<br><br>{stage["monster"]}</div>',
            unsafe_allow_html=True,
        )

        # HPバー
        st.write(f"魔物のHP：{max(combat['monster_hp'], 0)} / {combat['monster_max_hp']}")
        st.progress(max(combat["monster_hp"], 0) / combat["monster_max_hp"])
        st.write(f"あなたのHP：{max(combat['player_hp'], 0)} / {PLAYER_MAX_HP}")
        st.progress(max(combat["player_hp"], 0) / PLAYER_MAX_HP)

        st.markdown(f'<div class="battle-log">{chr(10).join(combat["log"][-8:])}</div>', unsafe_allow_html=True)

        if combat["result"] is None:
            st.write("**道具倉庫からアイテムを選んで攻撃しよう。**")
            st.caption("正しいアイテムはダメージを与えられるが、この階層に合わないアイテムは反撃を受けてしまう。")

            for item_id in stage["item_pool"]:
                label = ALL_ITEMS[item_id]
                is_used_correct = item_id in combat["used_correct"] and item_id in stage["correct"]
                cols = st.columns([4, 1])
                with cols[0]:
                    st.write(label)
                with cols[1]:
                    if is_used_correct:
                        st.write("✅ 使用済み")
                    else:
                        if st.button("攻撃", key=f"rpg_attack_{stage_idx}_{item_id}"):
                            item_name = label.split("（")[0]
                            if item_id in stage["correct"]:
                                combat["used_correct"].add(item_id)
                                combat["monster_hp"] -= MONSTER_HP_PER_ITEM
                                combat["log"].append(f"→「{item_name}」で攻撃！ 魔物に効果的だった。")
                                if combat["monster_hp"] <= 0:
                                    combat["result"] = "win"
                                    combat["log"].append("魔物を倒した！")
                            else:
                                combat["player_hp"] -= WRONG_ITEM_DAMAGE
                                combat["log"].append(f"→「{item_name}」で攻撃！ しかし効果がなく、反撃を受けた。")
                                if combat["player_hp"] <= 0:
                                    combat["result"] = "lose"
                                    combat["log"].append("力尽きてしまった…")
                            st.rerun()

            st.write("")
            if st.button("⚑ この階層をあきらめて装備を見直す", key=f"rpg_giveup_{stage_idx}"):
                reset_combat(stage_idx, stage)
                st.rerun()

        elif combat["result"] == "win":
            ss.rpg_cleared[stage_idx] = True
            st.success("勝利！ 魔物をたおした。")
            st.markdown(f'<div class="explain-box">{stage["explain"]}</div>', unsafe_allow_html=True)
            if st.button("次の階層へ →"):
                ss.rpg_stage += 1
                st.rerun()

        else:  # lose
            st.error("敗北してしまった。装備を見直して、もう一度挑もう。")
            if st.button("もう一度挑戦する"):
                reset_combat(stage_idx, stage)
                st.rerun()
    else:
        st.success("すべての階層の魔物をたおした。通信トラブルに立ち向かう知識と装備が身についたはずだ。")

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
    st.divider()
    st.checkbox("🎵 BGMを再生する", key="bgm_on")
    st.caption("ブラウザの仕様上、初回はこのチェックを入れる操作が必要です。")

if st.session_state.get("bgm_on"):
    render_bgm(st.session_state.mode)

if st.session_state.mode is None:
    show_home()
elif st.session_state.mode == "detective":
    show_detective()
elif st.session_state.mode == "rpg":
    show_rpg()