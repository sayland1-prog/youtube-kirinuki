import os
from typing import Optional

import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "")
_FROM_ADDRESS = os.environ.get("MAIL_FROM", "noreply@kirinuki.example.com")


def _clip_rows_html(clips: list[dict]) -> str:
    rows = []
    for i, clip in enumerate(clips, 1):
        rows.append(f"""
        <tr>
          <td style="padding:8px 0;font-weight:bold;">{i}. {clip.get('title', '')}</td>
        </tr>
        <tr>
          <td style="padding:4px 0 12px 0;">
            <a href="{clip.get('url_9x16', '#')}" style="margin-right:12px;">縦型(9:16)をダウンロード</a>
            <a href="{clip.get('url_16x9', '#')}" style="margin-right:12px;">横型(16:9)をダウンロード</a>
            <a href="{clip.get('caption_txt_url', '#')}">投稿文をダウンロード</a>
          </td>
        </tr>
        """)
    return "".join(rows)


def send_success_email(email: str, job_id: str, clips: list[dict], expires_at: Optional[str] = None) -> None:
    """切り抜き完了メールを送信する。"""
    expires_note = f"<p style='color:#888;font-size:13px;'>⚠️ ダウンロードリンクは {expires_at[:10] if expires_at else '1週間'} まで有効です。</p>" if expires_at else ""

    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#2563EB;">切り抜き動画が完成しました！</h2>
      <p>以下のリンクからダウンロードしてください。</p>
      {expires_note}
      <table width="100%" cellpadding="0" cellspacing="0">
        {_clip_rows_html(clips)}
      </table>
      <hr style="margin:24px 0;border:none;border-top:1px solid #eee;">
      <p style="color:#888;font-size:12px;">
        このメールは youtube-kirinuki サービスから自動送信されています。<br>
        ジョブID: {job_id}
      </p>
    </div>
    """

    # resend SDK v2 では "to" はリスト
    resend.Emails.send({
        "from": _FROM_ADDRESS,
        "to": [email],
        "subject": "【切り抜き完成】動画の準備ができました",
        "html": html,
    })


def send_failure_email(email: str, job_id: str, error_message: str) -> None:
    """処理失敗メールを送信する。"""
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <h2 style="color:#DC2626;">処理に失敗しました</h2>
      <p>申し訳ありません。動画の切り抜き処理中にエラーが発生しました。</p>
      <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;padding:16px;margin:16px 0;">
        <p style="margin:0;color:#B91C1C;">{error_message}</p>
      </div>
      <p>
        <a href="{os.environ.get('SERVICE_URL', 'https://kirinuki.example.com')}"
           style="background:#2563EB;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;">
          もう一度試す
        </a>
      </p>
      <hr style="margin:24px 0;border:none;border-top:1px solid #eee;">
      <p style="color:#888;font-size:12px;">
        このメールは youtube-kirinuki サービスから自動送信されています。<br>
        ジョブID: {job_id}
      </p>
    </div>
    """

    # resend SDK v2 では "to" はリスト
    resend.Emails.send({
        "from": _FROM_ADDRESS,
        "to": [email],
        "subject": "【エラー】切り抜き処理に失敗しました",
        "html": html,
    })
