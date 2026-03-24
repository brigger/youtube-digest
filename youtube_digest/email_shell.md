<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <style>
    body {{ margin:0; padding:0; background:#f4f4f4; font-family:Georgia,'Times New Roman',serif; color:#1a1a1a; }}
    .wrapper {{ max-width:680px; margin:32px auto; background:#fff; border-radius:6px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
    .header {{ background:#1a1a2e; padding:28px 36px; text-align:center; }}
    .header h1 {{ margin:0; font-family:Helvetica,Arial,sans-serif; font-size:22px; font-weight:700; color:#fff; letter-spacing:0.04em; text-transform:uppercase; }}
    .header p {{ margin:6px 0 0; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#9ba4c0; }}
    .body {{ padding:32px 36px; }}
    .toc {{ background:#f7f9fc; border-radius:4px; padding:18px 22px; margin-bottom:32px; }}
    .toc h3 {{ font-family:Helvetica,Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#888; margin:0 0 12px; }}
    .toc ul {{ margin:0; padding:0; list-style:none; }}
    .toc ul li {{ padding:5px 0; border-bottom:1px solid #e8ecf2; }}
    .toc ul li:last-child {{ border-bottom:none; }}
    .toc ul li > a {{ font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:700; color:#4a6fa5; text-decoration:none; }}
    .toc ul li > a:hover {{ text-decoration:underline; }}
    .toc ul li span {{ font-family:Helvetica,Arial,sans-serif; font-size:12px; color:#999; font-style:italic; display:block; margin-top:2px; }}
    .toc-items {{ margin:6px 0 2px 0; padding:0 0 0 14px; list-style:none; }}
    .toc-items li {{ font-family:Helvetica,Arial,sans-serif; font-size:12px; color:#555; padding:3px 0; border-bottom:none; }}
    .toc-items li a {{ font-size:12px; font-weight:600; color:#333; text-decoration:none; }}
    .toc-items li a:hover {{ text-decoration:underline; color:#4a6fa5; }}
    .topic-label {{ font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#fff; background:#4a6fa5; display:inline-block; padding:6px 14px; border-radius:3px; margin-bottom:20px; }}
    .back-to-top {{ font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#4a6fa5; text-decoration:none; display:block; text-align:right; margin-top:8px; margin-bottom:0; }}
    .item {{ border-left:3px solid #e8ecf2; padding:0 0 0 18px; margin-bottom:32px; }}
    .item h2 {{ font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:700; margin:0 0 4px; color:#1a1a2e; line-height:1.35; }}
    .item .meta {{ font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#888; margin-bottom:10px; }}
    .item .meta a {{ color:#4a6fa5; text-decoration:none; }}
    .item p {{ font-size:14px; line-height:1.65; margin:0 0 10px; color:#333; }}
    .item ul {{ margin:0; padding-left:20px; }}
    .item ul li {{ font-size:13.5px; line-height:1.6; color:#444; margin-bottom:5px; }}
    .divider {{ border:none; border-top:1px solid #e8ecf2; margin:36px 0; }}
    .sources {{ background:#f7f9fc; border-radius:4px; padding:18px 22px; margin-top:36px; }}
    .sources h3 {{ font-family:Helvetica,Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#888; margin:0 0 10px; }}
    .sources ul {{ margin:0; padding:0; list-style:none; }}
    .sources ul li {{ font-family:Helvetica,Arial,sans-serif; font-size:12px; color:#555; padding:3px 0; border-bottom:1px solid #e8ecf2; }}
    .sources ul li:last-child {{ border-bottom:none; }}
    .footer {{ padding:20px 36px; text-align:center; font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#aaa; background:#f7f9fc; border-top:1px solid #e8ecf2; }}
    .nothing {{ font-style:italic; color:#888; font-size:14px; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header" id="top">
      <h1>Daily Content Digest</h1>
      <p>{date}</p>
    </div>
    <div class="body">
      <div class="toc">
        <h3>Today's Topics</h3>
        <ul>
{toc_items}
        </ul>
      </div>
{sections}
      <div class="sources">
        <h3>Sources Checked</h3>
        <ul>
{sources_html}
        </ul>
      </div>
    </div>
    <div class="footer">Daily Digest &nbsp;&bull;&nbsp; {date} &nbsp;&bull;&nbsp; {total_n} items reviewed</div>
  </div>
</body>
</html>
