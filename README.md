# TS Videos processor

自分用に作った、m2ts形式録画ファイルをエンコードできる状態にするための前処理を行うソフトウェア

以下のことを行う

- tsDropChkによるドロップのチェックとDBへの記録
- tsSplitterによるファイルの分割とDBへの記録
- tssplitterによって分割されたtsファイルをAmatsukazeのキューに追加
- 分割されたtsファイルの内メインファイルを圧縮してNASに移動
- Amatsukazeでのエンコード後にエンコードで生成されたファイル群をNASに移動するためのバッチファイルとスクリプト

Amatsukazeに登録するtsファイルはmainSplittedFileFinderで選択抽出している。環境によってこれを変更する必要があると思われる。

利用のためには以下のソフトウェアが必要

- python3.9以上(Typingモジュールを使わすに型付けを行っているため)
- tsDropChk
- tsSplitter(最新版を推奨。2021/08現在1.28?)
- Amatsukaze

## 利用イメージ

```bash
pipenv shell

[pipenv shell]> python main.py "/path/to/video files directory/ OR /path/to/file"
```

## 注意事項

- 対象ファイルの拡張子は.m2tsである必要がある。
- 使用を始める前に、DDLをつかって適切にDBを用意する必要がある。mysqlに対応している。
- 使用を始める前に、tsDropChkとtsSplitter, AmatsukazeをPROJECT_ROOT/libraries/に配置する必要がある。配置すべきパスは、main/command/dropChk.pyとmain/command/tsSplitter.py, main/command/amatsukazeAddTask.pyのAPPLICATION_PATHを参照。
- 使用を始める前に、AmatsukazeServerが起動している必要がある。接続先ポート等も確認すること。
- 操作の途中でファイル名から録画日時、チャンネル、タイトルを取得する処理がある。そのため、動画ファイルのタイトルは以下の構造である必要がある。
  - \[210708-0030]\[BSBS13_1]\[ＢＳフジ・１８１]タイトル.m2ts
  - つまり\[]によって囲われたセクションが三つあり、その後にタイトルと拡張子が続く構造である。
  - \[]は、一つ目が録画（放送）日時。西暦下二ケタ、二ケタ月、二ケタ日、ハイフン、二ケタ時（24h）、二ケタ分である。
  - 二つ目は、チャンネル。物理チャンネル
  - 三つ目は、放送局名。
  - もし\[]によって囲われたセクションが四つ以上あった場合、それもすべて動画タイトルとみなして処理する。そのため、\[字]などが含まれる場合でも処理に問題はない。
- このプログラムを二プロセス以上同時に動作させたときにデータベースの内容が正しく更新される保証は、ない。
- このプログラムは元のtsファイルがtsSplitterによって分割されるとき2ファイルまたは1ファイルに分割されることを前提としている。環境によってこれが変更になるときはmainSplittedFileFinderを書き換える必要がある。
