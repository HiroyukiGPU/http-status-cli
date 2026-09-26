# HTTP STATUS CLI

複数URLのHTTPステータスと応答時間を一括表示します。

## インストール

Python 3.10以降が必要です。macOS / Linuxを主対象にしています。

```sh
pipx install git+https://github.com/HiroyukiGPU/http-status-cli.git
http-status --help
```

pipxを使わない場合は、仮想環境で `python -m pip install .` を実行できます。

## 使用例

```sh
http-status https://example.com https://github.com
http-status https://example.com --json
```

HEADで検査し、405/501の場合はGETへ切り替えます。リダイレクトを追跡した最終ステータスとURLを返します。時間は接続開始からレスポンスヘッダーまで。異常検出時は終了コード1。

## 開発と検証

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

終了コード: 通常0、検出結果ありは各コマンドの説明に従います。入力・通信・実行エラーは2、Ctrl+Cは130です。
データ保存を使うCLIは `~/.local/share/http-status-cli/` に保存します。`CLI_TOOLS_DATA_HOME` で保存先の親ディレクトリを変更できます。
ネットワークサービスにはタイムアウトを設定しています。APIの制限や応答によって失敗する場合はエラーを表示します。

## ライセンス

MIT。詳しくは [LICENSE](LICENSE) を参照してください。
