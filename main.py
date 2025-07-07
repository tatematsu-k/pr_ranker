import urllib.request
import urllib.parse
import urllib.error
import json
import os
from collections import defaultdict
import argparse
from datetime import datetime, timedelta
import time

# --- 設定 ---
# 1. GitHub パーソナルアクセストークン (PAT)
#    セキュリティのため、環境変数として設定することを強く推奨します。
#    例: export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#    PATは https://github.com/settings/tokens で生成できます。
#    必要なスコープ: 'repo' (private リポジトリの場合) または 'public_repo' (public リポジトリの場合)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# 2. 対象のGitHubリポジトリの所有者とリポジトリ名
REPO_OWNER = "FIXME"
REPO_NAME = "FIXME"

# --- 定数 ---
BASE_URL = "https://api.github.com"

# --- HTTPリクエストを行う関数 ---
def make_request(url, params=None):
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return None, e.code
    except urllib.error.URLError as e:
        return None, str(e)

# --- マージされたPRをすべて取得する関数 ---
def get_all_merged_prs(owner, repo, since_iso):
    all_merged_prs = []
    page = 1
    while True:
        url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": page
        }
        print(f"PR一覧のページ {page} を取得中... ({owner}/{repo})")
        response_data = make_request(url, params)
        if isinstance(response_data, tuple):
            return None, response_data[1]
        prs_on_page = json.loads(response_data)
        if not prs_on_page:
            break
        for pr in prs_on_page:
            merged_at = pr.get('merged_at')
            if merged_at and merged_at >= since_iso:
                all_merged_prs.append(pr)
        page += 1
    return all_merged_prs

# --- メイン処理 ---
def main():
    parser = argparse.ArgumentParser(description="GitHubのマージ済みPR集計ツール")
    parser.add_argument('--since', type=str, default=None, help='取得するPRの開始日(ISO8601, 例: 2024-04-01)。デフォルトは過去1ヶ月')
    args = parser.parse_args()

    if args.since:
        try:
            since_date = datetime.fromisoformat(args.since)
        except Exception:
            print("--since の日付形式が不正です。例: 2024-04-01")
            return
    else:
        since_date = datetime.now() - timedelta(days=30)
    since_iso = since_date.isoformat()

    if not GITHUB_TOKEN:
        print("エラー: GITHUB_TOKEN 環境変数が設定されていません。")
        print("GitHub パーソナルアクセストークン (PAT) を設定してください。")
        print("  例: export GITHUB_TOKEN='YOUR_PAT_HERE'")
        print("  PATは https://github.com/settings/tokens で生成できます。")
        return

    print(f"{REPO_OWNER}/{REPO_NAME} のマージされたプルリクエストを取得中... (since: {since_iso})")

    merged_prs = get_all_merged_prs(REPO_OWNER, REPO_NAME, since_iso)

    if isinstance(merged_prs, tuple):
        error_code = merged_prs[1]
        print(f"PRの取得中にエラーが発生しました: {error_code}")
        if error_code == 401:
            print("  認証エラーです。GITHUB_TOKEN が正しいか、必要なスコープが与えられているか確認してください。")
        elif error_code == 404:
            print("  リポジトリが見つかりません。リポジトリ名または所有者が正しいか確認してください。")
        elif error_code == 403:
            print("  レート制限または権限不足です。しばらく待つか、トークンの権限を確認してください。")
        return

    if not merged_prs:
        print(f"{REPO_OWNER}/{REPO_NAME} でマージされたプルリクエストは見つかりませんでした。")
        return

    print(f"\nマージされたPR {len(merged_prs)} 件を発見しました。作成者別に集計中...")

    author_counts = defaultdict(int)
    for i, pr in enumerate(merged_prs, 1):
        pull_number = pr.get('number')
        author = pr.get('user', {}).get('login', '不明な作成者')
        print(f"PR #{pull_number} の作成者を確認中... ({i}/{len(merged_prs)}) - 作成者: {author}")
        author_counts[author] += 1

    sorted_authors = sorted(author_counts.items(), key=lambda item: item[1], reverse=True)

    print("\n--- マージ済みPR数 (作成者別) ---")
    for author, count in sorted_authors:
        print(f"{author}: {count} 件")

if __name__ == "__main__":
    main()
