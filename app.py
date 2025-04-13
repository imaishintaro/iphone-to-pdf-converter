import streamlit as st
from PIL import Image
import io
import os
import datetime
import shutil
from reportlab.lib.pagesizes import A4, A5, B5, LETTER, LEGAL
from reportlab.pdfgen import canvas
import base64
from reportlab.lib.utils import ImageReader

# ディレクトリの確認と作成
UPLOAD_DIR = "uploads"
PDF_DIR = "generated_pdfs"

for directory in [UPLOAD_DIR, PDF_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# ページタイトルとアプリ説明
st.title("iPhone画像からPDF変換アプリ")
st.markdown("複数の画像をアップロードして、サイズと容量を指定したPDFに変換できます。")

# PDFサイズオプション
PAGE_SIZES = {
    "A4": A4,
    "A5": A5,
    "B5": B5,
    "LETTER": LETTER,
    "LEGAL": LEGAL
}

# サイドバー - PDF設定
st.sidebar.header("PDF設定")
page_size = st.sidebar.selectbox("PDFのサイズ", list(PAGE_SIZES.keys()))
orientation = st.sidebar.radio("PDFの向き", ["縦向き", "横向き"])

# PDFの容量設定
st.sidebar.header("容量設定")
image_quality = st.sidebar.slider("画像品質", 10, 100, 85, 5, 
                                help="低い値にすると容量が小さくなりますが、画質は下がります")
image_dpi = st.sidebar.slider("解像度(DPI)", 72, 300, 150, 
                           help="低い解像度にすると容量が小さくなります")

# 画像アップロード
st.write("### 画像をアップロード")
st.write("※ 合計サイズの上限は1GBです")
uploaded_files = st.file_uploader("画像をアップロード（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# サイズ確認関数
def check_files_size(files):
    total_size = sum(file.size for file in files)
    return total_size, total_size < 1_073_741_824  # 1GB = 1,073,741,824 bytes

# 処理関数
def create_pdf(images, page_size_name, orientation_name, quality, dpi):
    # ページサイズの取得
    page_size = PAGE_SIZES[page_size_name]
    if orientation_name == "横向き":
        page_size = (page_size[1], page_size[0])  # 幅と高さを入れ替え
    
    # PDFを作成
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size
    
    for img in images:
        # 画像のサイズ計算
        img_width, img_height = img.size
        
        # アスペクト比を保持したままのリサイズ
        ratio = min((width - 40) / img_width, (height - 40) / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        
        # 画像を中央に配置
        x = (width - new_width) / 2
        y = (height - new_height) / 2
        
        # 画像を一時的なバッファに保存して品質調整
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG", quality=quality)
        img_buffer.seek(0)
        
        # PDFに画像を配置
        img_reader = ImageReader(io.BytesIO(img_buffer.getvalue()))
        pdf.drawImage(img_reader, x, y, width=new_width, height=new_height)
        pdf.showPage()  # 新しいページ
    
    pdf.save()
    buffer.seek(0)
    return buffer

# PDFのダウンロードリンクを生成する関数
def get_download_link(buffer, filename="images_to_pdf.pdf"):
    b64 = base64.b64encode(buffer.getvalue()).decode()
    file_size = len(buffer.getvalue()) / (1024 * 1024)  # MB単位
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">PDFをダウンロード</a> (サイズ: {file_size:.2f} MB)'

# PDFをサーバーに保存する関数
def save_pdf_to_server(pdf_buffer, filename=None):
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdf_{timestamp}.pdf"
    
    filepath = os.path.join(PDF_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    return filepath

# メイン処理
if uploaded_files:
    # アップロードされたファイルの合計サイズをチェック
    total_size, is_size_ok = check_files_size(uploaded_files)
    
    if not is_size_ok:
        st.error(f"アップロードされた画像の合計サイズ ({total_size/(1024*1024*1024):.2f} GB) が1GBの制限を超えています。画像を減らすか、サイズを小さくしてください。")
    else:
        st.write(f"{len(uploaded_files)}枚の画像がアップロードされました（合計サイズ: {total_size/(1024*1024):.2f} MB）")
        
        # 画像のプレビュー
        st.subheader("画像プレビュー")
        cols = st.columns(3)
        
        images = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # PILで画像を開く
            img = Image.open(uploaded_file)
            images.append(img)
            
            # プレビュー表示（3列で表示）
            with cols[i % 3]:
                st.image(img, caption=f"画像 {i+1}", use_column_width=True)
        
        # PDFの生成
        if st.button("PDFを生成"):
            with st.spinner("PDFを生成中..."):
                try:
                    # PDFを生成
                    pdf_buffer = create_pdf(images, page_size, orientation, image_quality, image_dpi)
                    
                    # PDFファイルサイズを計算
                    pdf_size_mb = len(pdf_buffer.getvalue()) / (1024 * 1024)
                    
                    st.session_state.pdf_buffer = pdf_buffer  # セッションにPDFを保存
                    st.success(f"PDF生成が完了しました！ サイズ: {pdf_size_mb:.2f} MB")
                    
                    # ダウンロードリンクを表示
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"images_{page_size}_{orientation}_{timestamp}.pdf"
                    st.session_state.pdf_filename = filename
                    st.markdown(get_download_link(pdf_buffer, filename), unsafe_allow_html=True)
                    
                    # サーバー保存ボタンを表示
                    #st.session_state.show_save_button = True
                    
                except Exception as e:
                    st.error(f"PDFの生成中にエラーが発生しました: {e}")
                    st.exception(e)  # 詳細なエラー情報を表示
        
        # サーバー保存ボタン（PDFが生成されている場合のみ表示）
        
        #if st.session_state.get('show_save_button', False):
          # if st.button("サーバーに保存"):
           #     try:
            #        save_path = save_pdf_to_server(st.session_state.pdf_buffer, st.session_state.pdf_filename)
             #       st.success(f"PDFがサーバーに保存されました！ 保存先: {save_path}")
              #  except Exception as e:
               #     st.error(f"サーバーへの保存中にエラーが発生しました: {e}")
                #    '''

# 使い方の説明
if not uploaded_files:
    st.info("使い方: iPhoneで撮影した画像を選択し、サイドバーでPDFのサイズと容量設定を行ってください。")
    st.markdown("""
    ### このアプリでできること:
    - 複数の画像ファイルをアップロード（合計1GBまで）
    - PDFのサイズを選択 (A4, A5, B5, レター, リーガル)
    - PDFの向きを設定 (縦向き・横向き)
    - 画像の品質と解像度を調整して容量を制御
    - 生成したPDFをダウンロードまたはサーバーに保存
    """)

    # 保存済みPDFのリストを表示（オプション）
    if os.path.exists(PDF_DIR) and os.listdir(PDF_DIR):
        st.subheader("サーバーに保存済みのPDF")
        pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
        
        if pdf_files:
            for pdf_file in pdf_files:
                file_path = os.path.join(PDF_DIR, pdf_file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MBに変換
                st.write(f"📄 {pdf_file} ({file_size:.2f} MB)")
        else:
            st.write("保存済みのPDFはありません。")