# TS Videos processor

自分用に作った、m2ts形式録画ファイルをエンコードできる状態にするための前処理を行うソフトウェア

以下のことを行う

- tsDropChkによるドロップのチェックとDBへの記録
- tsSplitterによるファイルの分割とDBへの記録

これによって生成された分割済みファイルをエンコードするのだが、これは別途人力で行う。
現状、tsファイルが不正であったときにtsSplitterがどのような挙動をするのか把握しきれていないので、
このまま全自動化すると予期しない結果になる可能性があるため。

利用のためには以下のソフトウェアが必要

- python3.9以上(Typingモジュールを使わすに型付けを行っているため)
- tsDropChk
- tsSplitter(最新版を推奨。2021/08現在1.28?)

## 利用イメージ

```bash
python main.py "/path/to/video files directory/ OR /path/to/file path"
```

## 注意事項

- 対象ファイルの拡張子は.m2tsである必要がある。
- 使用を始める前に、DDLをつかってPROJECT_ROOT/database/database.sqliteファイルを作成する必要がある。
- 使用を始める前に、tsDropChkとtsSplitterをPROJECT_ROOT/libraries/に配置する必要がある。配置すべきパスは、command/dropChk.pyとcommand/tsSplitter.pyのAPPLICATION_PATHを参照。
