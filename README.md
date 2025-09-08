# sparebeat-player

Sparebeat の譜面ビューワ及びプレーヤー。  
僕が作って良いのだろうか... :thinking:

> [!INFO]
> すみません。半分 GPT 使ってます(コードの整理とかなんとかに)

> [!CAUTION]
> 一部の動作が、Sparebeat と異なります。
>
> - `startTime`の処理方法の違いにより、一部の譜面が FC 不可になる(症状が緩和するように調整予定です)
> - ブラーエフェクトが利用できない
> - レーンサイズ・SPEED の設定値が微妙に異なる(逐次修正予定です)

## 既知の問題

- Polygon (背景の画像) が正しく描画されない

## Todo

- [x] パーサーを書く
- [x] ファイルを分ける
- [x] 譜面の閲覧
- [ ] 操作

## 遊び方

[リリースを見ろ！！](https://github.com/nennneko5787/sparebeat-client/releases)  
<br>
なかったわ。

とりあえず

```
(mac/linux)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

(windows)
py -m venv venv
./venv/Scripts/Activate
pip install -r requirements.txt
py main.py
```

環境変数を作るのがミソ
