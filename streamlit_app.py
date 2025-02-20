import streamlit as st
import openai
import os
from PIL import Image
import pytesseract
import PyPDF2
import requests
from bs4 import BeautifulSoup

# OpenAI APIキーの設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_motivation(job_info, selected_interests, additional_interests, club_activities, other_achievements, correction=None):
    prompt = f"""
    あなたは高校生の志望動機作成をサポートするGPTです。
    次の情報を使って志望動機を作成してください。
    - 求人情報: {job_info}
    - 興味を持った点: {selected_interests}
    - 他の魅力的な点: {additional_interests}
    - 部活や習い事: {club_activities}
    - その他の頑張ったこと: {other_achievements}
    これは履歴書に記載する文章であるため書き言葉で丁寧な文章で出力します。
    出力する文章には時給や給与に関することは絶対に書きません。
    出力する前に文字数をカウントします。
    カウントした文字数が300字以上、400字以内ならそのまま出力します。400字以上ならばより簡潔な文章になるよう再出力し、300字未満の場合は再出力します。これを文字数の条件が満たせるまで繰り返します。
    """
    if correction:
        prompt += f"\nユーザーからの修正依頼: {correction}"

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"あなたは話すGPTです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def extract_points(motivation):
    prompt = f"次の志望動機から重要なポイントを3つ箇条書きで挙げてください。\n\n{motivation}"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは文章の要点を抽出するGPTです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def analyze_job_info(job_info):
    prompt = f"""
    求人情報として、応募を検討する場合に良いところと注意したほうが良いことをそれぞれ3つずつ簡潔に出力してください。就職活動をするのは10代で、社会人経験が乏しいことを想定して平易な言葉にしてください。
    
    求人情報:
    {job_info}
    
    良いところ:
    1.
    2.
    3.
    
    注意したほうが良いこと:
    1.
    2.
    3.
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは求人情報の分析をするGPTです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


#def read_image(image_file):
#    image = Image.open(image_file)
#    return pytesseract.image_to_string(image)

#def read_pdf(pdf_file):
#    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
#    text = ""
#    for page_num in range(pdf_reader.numPages):
#        page = pdf_reader.getPage(page_num)
#        text += page.extract_text()
#    return text

#def read_url(url):
#    response = requests.get(url)
#    soup = BeautifulSoup(response.content, 'html.parser')
#    return soup.get_text()

st.title("志望動機たたき台作成ロボ")
st.write("あなたが応募したい求人やあなたのことを教えてもらい、志望動機の下書きを作ります。")

# セッションステートの初期化
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.job_info = ""
    st.session_state.interests = []
    st.session_state.additional_interests = []
    st.session_state.other_interests = ""
    st.session_state.club_activities = ""
    st.session_state.other_achievements = ""
    st.session_state.motivation = ""
    st.session_state.analysis = ""
    

# 求人情報の入力
if st.session_state.step >= 0:
    st.subheader(f"求人情報を入力してください")
    input_method = st.selectbox("入力方法を選択してください", ["テキスト"])
    
    if input_method == "テキスト":
        st.session_state.job_info = st.text_area("求人情報の詳細をここに入力してください")
    
#    elif input_method == "画像":
#        image_file = st.file_uploader("画像ファイルをアップロードしてください", type=["png", "jpg", "jpeg"])
#        if image_file:
#            st.session_state.job_info = read_image(image_file)
#            st.write(st.session_state.job_info)
    
#    elif input_method == "PDF":
#        pdf_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])
#        if pdf_file:
#            st.session_state.job_info = read_pdf(pdf_file)
#            st.write(st.session_state.job_info)
    
#    elif input_method == "URL":
#        url = st.text_input("URLを入力してください")
#        if url:
#            st.session_state.job_info = read_url(url)
#            st.write(st.session_state.job_info)
    
    if st.button("ポイント分析を開始（少し時間がかかります）", key="step1_next"):
        st.session_state.analysis = analyze_job_info(st.session_state.job_info)
        st.session_state.step += 1

# 求人情報の分析結果表示
if st.session_state.step >= 1:
    st.subheader(f"求人情報のポイント分析")
    st.write(st.session_state.analysis)
    st.write(f"いかがですか？ここからはあなたのことを教えてください。")
    if st.button("次へ", key="step2_next"):
        st.session_state.step += 1

# 興味を持った点の選択
if st.session_state.step >= 2:
    st.subheader(f"どんなところに興味を持ちましたか？好きなだけ選んでください。")
    interests_options = ["給料が良い", "会社の場所が良い", "自分がしたい仕事", "すぐ働けそう", "得意なことが活かせそう", "生活スタイルに合ってる"]
    
    # チェックボックスの状態を保持する
    interests = []
    for option in interests_options:
        if st.checkbox(option, value=option in st.session_state.interests):
            interests.append(option)
    
    st.session_state.interests = interests
    
    if st.button("次へ", key="step3_next"):
        st.session_state.step += 1

# 他にも魅力に感じることの選択
if st.session_state.step >= 3:
    st.subheader(f"会社とのつながりはありますか？応募の後押しになったものはありますか？")
    additional_interests_options = ["先生にすすめられた", "職場見学に行って良いなと思った", "説明会に参加して良さそうだった", "先輩が働いている", "友人から良いと聞いた", "普段から利用している", "その他", "特にない"]

    # チェックボックスの状態を保持する
    additional_interests = []
    for option in additional_interests_options:
        if st.checkbox(option, value=option in st.session_state.additional_interests):
            additional_interests.append(option)
    
    st.session_state.additional_interests = additional_interests
    
    if "その他" in st.session_state.additional_interests:
        st.session_state.other_interests = st.text_input("どんなところに興味がありますか？")
    
    if st.button("次へ", key="step4_next"):
        st.session_state.step += 1

# 部活や習い事の入力
if st.session_state.step >= 4:
    st.subheader(f"部活や習い事はしていますか？")
    st.session_state.club_activities = st.text_input("している場合、どんなことをしているか教えてください（していないと答えても大丈夫です）")
    
    if st.button("次へ", key="step5_next"):
        st.session_state.step += 1

# その他の頑張ったことの入力
if st.session_state.step >= 5:
    st.subheader(f"勉強やアルバイト、資格など頑張ったことがありますか？")
    st.session_state.other_achievements = st.text_input("頑張ったことを教えてください（思いつかないときはその通り答えてください）")
    
    if st.button("志望動機を書き出す（少し時間がかかります）", key="step6_next"):
        st.session_state.step += 1

# 志望動機の生成
if st.session_state.step >= 6:
    if st.session_state.motivation == "":
        st.session_state.motivation = generate_motivation(
        st.session_state.job_info,
        st.session_state.interests,
        st.session_state.additional_interests,
        st.session_state.club_activities,
        st.session_state.other_achievements,
        st.session_state.analysis
    )
    st.subheader("こんな志望動機はどうでしょう？")
    st.write(st.session_state.motivation)

    # ポイントの表示
    points = extract_points(st.session_state.motivation)
    st.subheader("志望動機のポイント")
    st.write(points)

    # 次の行動の選択肢
    st.subheader("次の行動を選択してください")
    next_action = st.radio("選択肢", ["文章を直したい"])

    # 作業9: 文章の修正
    if next_action == "文章を直したい":
        correction = st.text_input("どこが気になりましたか？")
        if st.button("修正する"):
            updated_motivation = generate_motivation(
                st.session_state.job_info,
                st.session_state.interests,
                st.session_state.additional_interests,
                st.session_state.club_activities,
                st.session_state.other_achievements,
                st.session_state.analysis,
                #correction
            )
            st.session_state.motivation = updated_motivation
            st.write(updated_motivation)
            points = extract_points(updated_motivation)
            st.subheader("志望動機のポイント")
            st.write(points)

        # 作業10: リセットとアンケート
        if st.button("最初からやり直す"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()
            
        st.write("お手伝いはここまでです。内容にまちがいがないか、先生や周りの大人にも見せて反応を聞いてみましょう。")
        st.write("[最短1分で終わるアンケートにご協力ください！]( https://forms.gle/TJPW7RF6FiusqiAX7)")
