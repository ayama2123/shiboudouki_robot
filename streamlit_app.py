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

# キャラクターの選択肢と口調
#characters = {
#    "普通": "丁寧な口調",
#    "やさしく寄り添い": "優しく寄り添う口調",
#    "ギャル": "ギャルのような口調",
#    "関西弁": "関西弁の口調"
#}

#character_tone = {
#    "普通": "丁寧に",
#    "やさしく寄り添い": "優しく寄り添って",
#    "ギャル": "ギャルっぽく",
#    "関西弁": "関西弁で"
#}

def generate_motivation(job_info, selected_interests, additional_interests, club_activities, other_achievements, correction=None):
    prompt = f"""
    あなたは高校生の志望動機作成をサポートするGPTです。
    次の情報を使って志望動機を作成してください。
    - 求人情報: {job_info}
    - 興味を持った点: {selected_interests}
    - 他の魅力的な点: {additional_interests}
    - 部活や習い事: {club_activities}
    - その他の頑張ったこと: {other_achievements}
    """
    if correction:
        prompt += f"\nユーザーからの修正依頼: {correction}"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"あなたは話すGPTです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def extract_points(motivation):
    prompt = f"次の志望動機から重要なポイントを3つ箇条書きで挙げてください。\n\n{motivation}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは文章の要点を抽出するGPTです。"},
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

# セッションステートの初期化
if 'step' not in st.session_state:
    st.session_state.step = 0
    #st.session_state.character = ""
    st.session_state.job_info = ""
    st.session_state.interests = []
    st.session_state.additional_interests = []
    st.session_state.other_interests = ""
    st.session_state.club_activities = ""
    st.session_state.other_achievements = ""
    st.session_state.motivation = ""
    
# キャラクターの選択
#if st.session_state.step == 0:
#    st.subheader("キャラクターを選択してください")
#    st.session_state.character = st.selectbox("キャラクター", list(characters.keys()))
#    if st.button("次へ"):
#        st.session_state.step += 1

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
    
    if st.button("次へ", key="step1_next"):
        st.session_state.step += 1

# 興味を持った点の選択
if st.session_state.step >= 1:
    st.subheader(f"会社のどんなところに興味を持ちましたか？")
    st.session_state.interests = st.multiselect("複数選択してください", ["給料が良い", "会社の場所が良い", "自分がしたい仕事", "得意なことが活かせそうだ"])
    
    if st.button("次へ", key="step2_next"):
        st.session_state.step += 1

# 他にも魅力に感じることの選択
if st.session_state.step >= 2:
    st.subheader(f"他にも魅力に感じることがありますか？")
    st.session_state.additional_interests = st.multiselect("複数選択してください", ["先生に勧められた", "職場見学に行って良いなと思った", "説明会に参加して良さそうだった", "先輩が働いている", "その他"])
    if "その他" in st.session_state.additional_interests:
        st.session_state.other_interests = st.text_input("どんなところに興味がありますか？")
    
    if st.button("次へ", key="step3_next"):
        st.session_state.step += 1

# 部活や習い事の入力
if st.session_state.step >= 3:
    st.subheader(f"部活や習い事はしていますか？")
    st.session_state.club_activities = st.text_input("している場合、どんなことをしているか教えてください（していない場合はしていないと入力してください）")
    
    if st.button("次へ", key="step4_next"):
        st.session_state.step += 1

# その他の頑張ったことの入力
if st.session_state.step >= 4:
    st.subheader(f"勉強やアルバイト、資格など頑張ったことがありますか？")
    st.session_state.other_achievements = st.text_input("頑張ったことを教えてください（思いつかない場合はそれでも良いと入力してください）")
    
    if st.button("志望動機を書き出す（少し時間がかかります）", key="step5_next"):
        st.session_state.step += 1

# 志望動機の生成
if st.session_state.step >= 5:
    if st.session_state.motivation == "":
        st.session_state.motivation = generate_motivation(
        #st.session_state.character,
        st.session_state.job_info,
        st.session_state.interests,
        st.session_state.additional_interests,
        st.session_state.club_activities,
        st.session_state.other_achievements
    )
    st.subheader("生成された志望動機")
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
                #st.session_state.character,
                st.session_state.job_info,
                st.session_state.interests,
                st.session_state.additional_interests,
                st.session_state.club_activities,
                st.session_state.other_achievements,
                correction
            )
            st.session_state.motivation = updated_motivation
            st.write(updated_motivation)
            points = extract_points(updated_motivation)
            st.subheader("志望動機のポイント")
            st.write(points)
#    else:
#        st.subheader("生成された志望動機を保存または送信しますか？")
#        if st.button("テキストファイルとして保存"):
#            with open("motivation.txt", "w") as file:
#                file.write(st.session_state.motivation)
#            st.success("志望動機がmotivation.txtとして保存されました。")
        
#        if st.button("メールで送信"):
#            st.text_input("送信先のメールアドレスを入力してください")
#            if st.button("送信"):
#                st.success("メール送信機能はまだ実装されていません。")

#        st.write("お手伝いはここまでです。先生や周りの大人に確認してみてください。")
