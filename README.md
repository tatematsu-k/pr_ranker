# pr_ranker

GitHub のマージ済みプルリクエストを作成者ごとに集計するツールです。

## 機能

- 指定リポジトリのマージ済み PR を取得し、作成者ごとに件数を集計
- 期間指定（デフォルトは過去 1 ヶ月）
- Docker 対応
- .envrc による環境変数管理

## 必要なもの

- GitHub パーソナルアクセストークン（PAT）
  - スコープ: `repo`（private の場合）または `public_repo`（public の場合）
- Python 3.8 以降（ローカル実行時）
- Docker（推奨）

## セットアップ

1. `.envrc` ファイルをプロジェクトルートに作成し、以下のように記載してください。

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

2. 必要に応じて `main.py` 内の `REPO_OWNER` と `REPO_NAME` を対象リポジトリに書き換えてください。

## 使い方

### Docker で実行

1. イメージをビルド

```sh
make build
```

2. ローカルの `main.py` と `.envrc` を同期して実行

```sh
make exec
```

### 直接 Python で実行

```sh
export $(grep -v '^#' .envrc | xargs)
python main.py
```

### 期間指定

`--since` オプションで ISO8601 形式の日付を指定できます。

```sh
make exec -- --since 2024-04-01
```

または

```sh
python main.py --since 2024-04-01
```

## 注意事項

- GitHub API のレート制限にご注意ください。
- PAT の権限不足やリポジトリ名の間違いにご注意ください。

## ライセンス

MIT
