<p align="left">
    <a href="README.md">
        中文
    </a>
    <span> • </span>
    <span>
        日本語
    </span>
    <span> • </span>
    <a href="README_en.md">
        English
    </a>
</p>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR">
    <img width="200" height="128" src="https://tupian.li/images/2022/10/27/icon---256.png" alt="Umi-OCR">
  </a>
</p>

<h1 align="center">Umi-OCR</h1>

<p align="center">
  <a href="https://github.com/hiroi-sora/Umi-OCR/releases/latest">
    <img src="https://img.shields.io/github/v/release/hiroi-sora/Umi-OCR?style=flat-square" alt="Umi-OCR">
  </a>
  <a href="License">
    <img src="https://img.shields.io/github/license/hiroi-sora/Umi-OCR?style=flat-square" alt="LICENSE">
  </a>
  <a href="#ダウンロード">
    <img src="https://img.shields.io/github/downloads/hiroi-sora/Umi-OCR/total?style=flat-square" alt="ダウンロード">
  </a>
  <a href="https://star-history.com/#hiroi-sora/Umi-OCR">
    <img src="https://img.shields.io/github/stars/hiroi-sora/Umi-OCR?style=flat-square" alt="スター">
  </a>
  <a href="https://github.com/hiroi-sora/Umi-OCR/forks">
    <img src="https://img.shields.io/github/forks/hiroi-sora/Umi-OCR?style=flat-square" alt="フォーク">
  </a>
  <a href="https://hosted.weblate.org/engage/umi-ocr/">
    <img src="https://hosted.weblate.org/widget/umi-ocr/svg-badge.svg" alt="翻译状态">
  </a>
</p>

<div align="center">
  <strong>無料、オープンソース、バッチオフラインOCRソフトウェア</strong><br>
  <sub>Windows7 x64以上と互換性があります</sub>
</div><br>

- **無料**: このプロジェクトのすべてのコードはオープンソースで完全に無料です。
- **便利**: 解凍して使用し、オフラインで実行し、ネットワークは必要ありません。
- **効率的**: 高効率のオフラインOCRエンジンが付属しています。コンピュータのパフォーマンスが十分であれば、オンラインOCRサービスよりも速くなることがあります。
- **柔軟**: カスタマイズ可能なインターフェースをサポートし、コマンドラインやHTTP APIなど、複数の呼び出し方法をサポートします。

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ec301b55.png" alt="1-タイトル-1.png" style="width: 80%;"></p>

![1-タイトル-2.png](https://tupian.li/images/2023/11/19/6559909fdeeba.png)

## ソースコードの使用:

開発者は、進む前に[プロジェクトのビルド](#プロジェクトのビルド)を読むべきです。

## リリースのダウンロード:

- **GitHub** https://github.com/hiroi-sora/Umi-OCR/releases/latest
- **Source Forge** https://sourceforge.net/projects/umi-ocr
- **Lanzou (蓝奏云)** https://hiroi-sora.lanzoul.com/s/umi-ocr

## はじめに

ソフトウェアリリースパッケージは、`.7z`圧縮形式または自己解凍`.7z.exe`パッケージで利用可能です。自己解凍パッケージは、圧縮ソフトウェアがインストールされていないコンピューターでファイルを抽出するために使用できます。

このソフトウェアはインストールを必要としません。抽出後、`Umi-OCR.exe`をクリックしてプログラムを開始します。

問題が発生した場合は、[Issue](https://github.com/hiroi-sora/Umi-OCR/issues)を提出してください。最善を尽くしてサポートします。

## インターフェース言語

Umi-OCRは、インターフェースの複数の言語をサポートしています。ソフトウェアを初めて開くと、コンピューターのシステム設定に基づいて自動的に言語が切り替わります。

言語を手動で切り替える必要がある場合は、以下の図を参照してください。`全局设置`→`语言/Language`。

<p align="center"><img src="https://tupian.li/images/2023/11/19/65599c3f9e600.png" alt="1-タイトル-1.png" style="width: 80%;"></p>

### 翻訳を手伝ってください

Weblateオンラインで翻訳作業に参加できます:

https://hosted.weblate.org/engage/umi-ocr/

## タブインターフェース

Umi-OCR v2は、一連の柔軟で使いやすい**タブインターフェース**で構成されています。好みに応じて必要なタブインターフェースを開くことができます。

タブバーの左上隅を使用して**ウィンドウ常に最前面**を切り替えることができます。右上隅は、日常使用中の偶発的な閉鎖を防ぐために**タブインターフェースをロック**するために使用できます。

### スクリーンショットOCR

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecb4dfb4.png" alt="2-スクリーンショット-1.png" style="width: 80%;"></p>

**スクリーンショットOCR**: このページを開いた後、キーボードショートカットを使用してスクリーンショットをキャプチャし、画像内のテキストを認識することができます。
- 左側の画像プレビューパネルを使用して、マウスでテキストを選択してコピーすることができます。
- 右側の認識レコードパネルを使用して、テキストを編集し、複数のレコードを選択してコピーすることができます。
- 他の場所から画像をコピーしてUmi-OCRに貼り付け、認識することもサポートしています。

#### 段落マージ

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecc62ac9.png" alt="2-スクリーンショット-2.png" style="width: 80%;"></p>

**OCRテキスト後処理 - 段落マージ**について: この機能は、OCR結果のレイアウトと順序を整理し、テキストを読みやすく使用しやすくすることができます。プリセットスキームは以下の通りです。
  - **単一行**: 同じ行上のテキストをマージします。ほとんどのシナリオに適しています。
  - **複数行 - 自然な段落**: 同じ段落に属するテキストを知的に認識してマージします。ほとんどのシナリオに適しており、上記の図に示されています。
  - **複数行 - コードブロック**: テキストの元のインデントとスペーシングを復元しようとします。コードスニペットやスペースを保持する必要があるシーンを認識するのに適しています。
  - **縦書きレイアウト**: 縦書きレイアウトに適しています。縦書き認識もサポートするモデルライブラリと併用する必要があります。

---

### バッチOCR

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecdc5197.png" alt="3-バッチ-1.png" style="width: 80%;"></p>

**バッチOCR**: このページでは、ローカル画像をバッチでインポートして認識することがサポートされています。
- 認識されたコンテンツは、txt/jsonl/md/csv(Excel)などのさまざまな形式で保存できます。
- `テキスト後処理`技術をサポートし、同じ自然な段落に属するテキストを認識してマージすることができます。また、コードブロックや縦書きテキストなど、複数の処理スキームもサポートしています。
- 一度に処理できる画像の数に制限はなく、タスクを完了した後、ソフトウェアは自動的にシャットダウンまたはスリープすることができます。
 
#### 無視領域

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecbc0021.png" alt="3-バッチ-2.png" style="width: 80%;"></p>

**OCRテキスト後処理 - 無視領域**について: これは、バッチOCRの特別な機能で、画像内の望ましくないテキストを除外するために使用されます。
- 無視領域エディタは、バッチ認識ページ設定の右側の列でアクセスできます。
- 上記の例のように、画像の上部と右下隅に複数の透かし/LOGOがあります。これらの画像がバッチで認識される場合、透かしは認識結果に干渉します。
- 右マウスボタンを押し続けて、複数の長方形ボックスを描画します。これらのエリア内のテキストは、タスク中に無視されます。
- 長方形ボックスをできるだけ大きく描画し、透かしのすべての可能な位置を完全に包むようにしてください。

---

### バルクドキュメント認識

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ecc8bfd4.png" alt="" style="width: 80%;"></p>

---

### QRコード

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed01f5b2.png" alt="4-QRコード-1.png" style="width: 80%;"></p>

**スキャンコード**:
- スクリーンショットをキャプチャしたり、貼り付けたり、ローカル画像をドラッグして、QRコードやバーコードを読み取ることができます。
- 1つの画像で複数のコードをサポートします。
- 以下の19のプロトコルをサポートします:

`Aztec`,`Codabar`,`Code128`,`Code39`,`Code93`,`DataBar`,`DataBarExpanded`,`DataMatrix`,`EAN13`,`EAN8`,`ITF`,`LinearCodes`,`MatrixCodes`,`MaxiCode`,`MicroQRCode`,`PDF417`,`QRCode`,`UPCA`,`UPCE`,

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed001437.png" alt="4-QRコード-2.png" style="width: 80%;"></p>

**コード生成**:
- テキストを入力してQRコード画像を生成します。
- **誤り訂正レベル**などのパラメータを含む19のプロトコルをサポートします。

---

### グローバル設定

<p align="center"><img src="https://tupian.li/images/2024/03/27/66040ed16f4e0.png" alt="5-グローバル設定-1.png" style="width: 80%;"></p>

**グローバル設定**: ここでは、ソフトウェアのグローバルパラメータを調整できます。一般的な機能には、以下が含まれます:
- ショートカットを一度に追加するか、自動起動を設定します。
- インターフェースの**言語**を変更します。Umiは繁体字中国語、英語、日本語などの言語をサポートしています。
- インターフェースの**テーマ**を切り替えます。Umiには複数のライト/ダークテーマがあります。
- インターフェーステキストの**フォントサイズ**と**フォント**を調整します。
- OCRプラグインを切り替えます。
- **レンダラー**: ソフトウェアインターフェースは、デフォルトでGPU加速レンダリングをサポートしています。画面のちらつきやUIの位置ずれが発生する場合は、`インターフェースと外観` → `レンダラー`に移動して、異なるレンダリングスキームに切り替えるか、ハードウェアアクセラレーションをオフにしてみてください。

---

## APIの使用:

- コマンドラインマニュアル: [README_CLI.md](docs/README_CLI.md)
- HTTP APIマニュアル: [README_HTTP.md](docs/README_HTTP.md)

## プロジェクト構造について

### リポジトリ:

- [メインリポジトリ](https://github.com/hiroi-sora/Umi-OCR) 👈
- [プラグインリポジトリ](https://github.com/hiroi-sora/Umi-OCR_plugins)
- [Winランタイムライブラリ](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)

## プロジェクトのビルド

### ステップ0: (オプション) このプロジェクトをフォークする

### ステップ1: コードをダウンロードする

以下のいずれかを選択してください:
- フォークしたリポジトリをローカルマシンにプルする
- このリポジトリのzipソースコードパッケージをダウンロードする
- このリポジトリをクローンする

### 次のステップ:

対応するプラットフォームの開発/ランタイム環境デプロイメントを完了するには、以下のリポジトリに進んでください。

このプロジェクトには、非常にシンプルなワンクリックパッケージングスクリプトもあり、以下のリポジトリで見つけることができます。

- [Windows](https://github.com/hiroi-sora/Umi-OCR_runtime_windows)
- クロスプラットフォームサポートは開発中です。

## [変更ログ](CHANGE_LOG.md)
