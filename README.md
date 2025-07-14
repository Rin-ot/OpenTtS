# 🔊 OpenTtS

OpenTtSは誰でも利用できるオープンソースの読み上げボットです。

---

## ♻️ 公開中のボットを使用する

１． サーバーに追加する  

**[ここ](https://r.r7x.jp/opentts)** から、現在公開中のOpenTtSをサーバーに導入できます。

２． 権限を設定する

<img src="http://r7x.jp/opentts/verify_permission.png" width=400></img>

※権限設定のうち、**管理者**の権限は必須ではありません。

３． 読み上げを使用する

読み上げてほしいテキストチャンネルで **`読み上げ開始`** と送信するか、 **`/vc`** コマンドを使用すると自動で読み上げが開始されます。

---

## 🔨 セルフホスト（自己環境で実行）

１． 実行環境を構築する  

```bash
$ python3 -m venv OpenTtS_venv
$ source OpenTtS_venv/bin/activate
(OpenTtS_venv) $ python3 -m pip install -r requirements.txt
```

２． OpenTtS本体を実行する

```bash
(OpenTtS_venv) $ python3 main.py
```

### ⚠️ 注意

OpenTtSは以下各種音声合成エンジン・ライブラリを使用しています。  
これらを別プロセスで稼働させるか、サードパーティ製APIを使用しない場合読み上げに問題が生じることがあります。  
>  
１． [gTTS](https://pypi.org/project/gTTS/) (Google Text-to-Speach)  
２． [VOICEVOX](https://voicevox.hiroshiba.jp/) (© Hiroshiba Kazuyuki)  
３． [COEIROINK](https://coeiroink.com/) (© [Shirowanisan](https://x.com/shirowanisan))  
４． [Open JTalk](https://open-jtalk.sourceforge.net/) *本リポジトリ内ではapt版を使用 (© [名古屋工業大学](https://www.nitech.ac.jp/))