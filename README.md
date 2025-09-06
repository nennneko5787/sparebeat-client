# sparebeat-client

作って良いのだろうか... :thinking:

> [!WARNING]
> 現在 Southern Cross がプレーできない対策として一部のエラーを抑制していますが、将来のバージョンでこの処理を削除する予定です。

> [!CAUTION]
> 一部の動作が、Sparebeat と異なります。
>
> - `startTime`の処理方法の違いにより、一部の譜面が FC 不可になる(症状が緩和するように調整予定です)
> - ブラーエフェクトが利用できない
> - レーンサイズ・SPEED の設定値が微妙に異なる(逐次修正予定です)
> - 一部の曲の速度変化・BPM 変化が正常に行われない(BPM 変化が行われなかった場合、譜面のズレが発生する)
> - 一部の曲で拍線が Sparebeat と同じように描画されない

## 既知の問題

- Polygon (背景の画像) が正しく描画されない

## Todo

- [x] パーサーを書く
- [x] ファイルを分ける
- [ ] 譜面の閲覧
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
