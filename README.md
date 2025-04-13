# iPhone画像からPDF変換アプリ

iPhoneで撮影した画像を簡単にPDFに変換するStreamlitアプリケーションです。

## 主な機能

- 複数の画像ファイルをアップロード（合計1GBまで）
- PDFのサイズを選択 (A4, A5, B5, レター, リーガル)
- PDFの向きを設定 (縦向き・横向き)
- 画像の品質と解像度を調整して容量を制御
- 生成したPDFをダウンロードまたはサーバーに保存

## 使い方

1. iPhoneで撮影した画像を選択
2. サイドバーでPDFのサイズと容量設定を行う
3. 「PDFを生成」ボタンをクリック
4. 生成されたPDFをダウンロードまたはサーバーに保存

## インストール方法

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 開発環境

- Python 3.8+
- Streamlit 1.28.0
- Pillow 10.0.0
- ReportLab 4.0.4
