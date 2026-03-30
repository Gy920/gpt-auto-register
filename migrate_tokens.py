"""
Token 迁移脚本 - 为缺少 id_token 的文件补上兼容 id_token
用法: python migrate_tokens.py [--token-dir codex_tokens]
"""

import os
import sys
import json
import base64
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta


def _decode_jwt_payload(token: str) -> dict:
    """解码 JWT payload"""
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        payload_json = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_json)
    except Exception:
        return {}


def _generate_compatible_id_token(email: str, chatgpt_account_id: str, chatgpt_user_id: str, exp_timestamp: int = None) -> str:
    """生成兼容的 id_token（最小 JWT 结构，用于 CPA 额度解析）"""
    if not exp_timestamp:
        exp_timestamp = int(time.time()) + 3600 * 24 * 7  # 7天有效期

    # JWT header
    header = {"alg": "none", "typ": "JWT"}

    # JWT payload - 包含 CPA 需要的所有字段
    payload = {
        "email": email,
        "exp": exp_timestamp,
        "https://api.openai.com/auth": {
            "chatgpt_account_id": chatgpt_account_id,
            "chatgpt_user_id": chatgpt_user_id,
            "plan_type": "chatgptplus"
        }
    }

    # Base64URL 编码（无签名）
    def b64url_encode(data):
        json_str = json.dumps(data, separators=(',', ':'))
        return base64.urlsafe_b64encode(json_str.encode()).rstrip(b'=').decode()

    header_b64 = b64url_encode(header)
    payload_b64 = b64url_encode(payload)

    # 返回无签名的 JWT（CPA 只解析 payload，不验证签名）
    return f"{header_b64}.{payload_b64}."


def migrate_token_file(token_path: str, dry_run: bool = False) -> dict:
    """迁移单个 token 文件"""
    result = {"file": token_path, "status": "skipped", "changes": []}

    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token_data = json.load(f)
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"读取失败: {e}"
        return result

    email = token_data.get("email", Path(token_path).stem)
    access_token = token_data.get("access_token", "")
    id_token = token_data.get("id_token", "")
    refresh_token = token_data.get("refresh_token", "")
    session_token = token_data.get("session_token", "")

    # 优先从顶层获取 account_id
    chatgpt_account_id = token_data.get("chatgpt_account_id") or token_data.get("account_id", "")
    chatgpt_user_id = token_data.get("chatgpt_user_id", "")

    # 从 id_token 解析用户信息（最可靠）
    if id_token:
        payload = _decode_jwt_payload(id_token)
        auth_info = payload.get("https://api.openai.com/auth", {})
        if not chatgpt_account_id:
            chatgpt_account_id = auth_info.get("chatgpt_account_id", "")
        if not chatgpt_user_id:
            chatgpt_user_id = auth_info.get("chatgpt_user_id", "")

    # 从 access_token 解析用户信息（备选）
    if not chatgpt_account_id and access_token:
        payload = _decode_jwt_payload(access_token)
        auth_info = payload.get("https://api.openai.com/auth", {})
        chatgpt_account_id = auth_info.get("chatgpt_account_id", "")
        if not chatgpt_user_id:
            chatgpt_user_id = auth_info.get("chatgpt_user_id", "")

    # 如果仍然没有 id_token 但有 account_id，生成兼容的
    if not id_token and chatgpt_account_id:
        exp_timestamp = None
        if access_token:
            payload = _decode_jwt_payload(access_token)
            exp_timestamp = payload.get("exp")
        id_token = _generate_compatible_id_token(email, chatgpt_account_id, chatgpt_user_id, exp_timestamp)

    if not chatgpt_account_id:
        result["status"] = "skipped"
        result["error"] = "缺少 chatgpt_account_id"
        return result

    changes = []

    # 补全顶层字段
    if id_token and not token_data.get("id_token"):
        token_data["id_token"] = id_token
        changes.append("补全 id_token")

    if not token_data.get("chatgpt_account_id"):
        token_data["chatgpt_account_id"] = chatgpt_account_id
        changes.append("补全 chatgpt_account_id")

    if chatgpt_user_id and not token_data.get("chatgpt_user_id"):
        token_data["chatgpt_user_id"] = chatgpt_user_id
        changes.append("补全 chatgpt_user_id")

    if session_token and not token_data.get("session_token"):
        token_data["session_token"] = session_token
        changes.append("补全 session_token")

    # 补全 credentials 字段
    credentials = token_data.get("credentials", {})
    credentials_updated = False

    if not credentials:
        credentials = {}
        credentials_updated = True

    if access_token and not credentials.get("access_token"):
        credentials["access_token"] = access_token
        credentials_updated = True

    if refresh_token and not credentials.get("refresh_token"):
        credentials["refresh_token"] = refresh_token
        credentials_updated = True

    if id_token and not credentials.get("id_token"):
        credentials["id_token"] = id_token
        credentials_updated = True

    if chatgpt_account_id and not credentials.get("chatgpt_account_id"):
        credentials["chatgpt_account_id"] = chatgpt_account_id
        credentials_updated = True

    if chatgpt_user_id and not credentials.get("chatgpt_user_id"):
        credentials["chatgpt_user_id"] = chatgpt_user_id
        credentials_updated = True

    if session_token and not credentials.get("session_token"):
        credentials["session_token"] = session_token
        credentials_updated = True

    if credentials_updated:
        token_data["credentials"] = credentials
        changes.append("补全 credentials")

    if not changes:
        result["status"] = "ok"
        result["message"] = "无需修改"
        return result

    result["changes"] = changes

    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"将修改: {', '.join(changes)}"
    else:
        try:
            with open(token_path, "w", encoding="utf-8") as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            result["status"] = "updated"
            result["message"] = f"已修改: {', '.join(changes)}"
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"写入失败: {e}"

    return result


def migrate_all_tokens(token_dir: str, dry_run: bool = False, reupload: bool = False):
    """迁移所有 token 文件"""
    token_path = Path(token_dir)
    if not token_path.exists():
        print(f"[Error] Token 目录不存在: {token_dir}")
        return

    json_files = list(token_path.glob("*.json"))
    print(f"[Migrate] 找到 {len(json_files)} 个 token 文件")

    if dry_run:
        print("[Migrate] DRY RUN 模式 - 不会实际修改文件")

    stats = {"updated": 0, "skipped": 0, "error": 0}
    updated_files = []

    for token_file in json_files:
        result = migrate_token_file(str(token_file), dry_run)
        status = result["status"]

        if status == "updated" or status == "dry_run":
            stats["updated"] += 1
            if status == "updated":
                updated_files.append(str(token_file))
            print(f"  [{status.upper()}] {token_file.name}: {result.get('message', '')}")
        elif status == "error":
            stats["error"] += 1
            print(f"  [ERROR] {token_file.name}: {result.get('error', '')}")
        else:
            stats["skipped"] += 1

    print(f"\n[Migrate] 完成: 更新 {stats['updated']} / 跳过 {stats['skipped']} / 错误 {stats['error']}")

    # 如果需要重新上传到 CPA
    if reupload and updated_files and not dry_run:
        print(f"\n[Migrate] 开始重新上传 {len(updated_files)} 个文件到 CPA...")
        try:
            from sync_manager import AccountSyncManager
            sync_mgr = AccountSyncManager()

            success = 0
            failed = 0
            for token_file in updated_files:
                if sync_mgr.upload_to_cpa(token_file):
                    success += 1
                    print(f"  [OK] {Path(token_file).name}")
                else:
                    failed += 1
                    print(f"  [FAIL] {Path(token_file).name}")

            print(f"\n[Migrate] CPA 上传完成: 成功 {success} / 失败 {failed}")
        except Exception as e:
            print(f"[Migrate] CPA 上传失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="Token 迁移工具")
    parser.add_argument("--token-dir", default="codex_tokens", help="Token 目录")
    parser.add_argument("--dry-run", action="store_true", help="只检查，不修改")
    parser.add_argument("--reupload", action="store_true", help="修改后重新上传到 CPA")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_dir = args.token_dir if os.path.isabs(args.token_dir) else os.path.join(base_dir, args.token_dir)

    migrate_all_tokens(token_dir, args.dry_run, args.reupload)


if __name__ == "__main__":
    main()
