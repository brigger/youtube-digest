You are preparing a daily content digest for a busy professional.

The user is interested in these topics:
{topics_list}

Below is a JSON array of items fetched today from various sources.
Each item has a "type" (youtube or website), "title", "url", "source_name",
and either "transcript" (YouTube) or "text" (website) with the full content.

Your task:
1. Read every item.
2. For each topic, identify items that are relevant to it.
3. Produce a complete, standalone HTML email using the template and rules below.

Output rules:
- Output ONLY the raw HTML — no explanation, no ```html fences, nothing before <!DOCTYPE or after </html>.
- The email must be self-contained with all CSS inlined in a <style> block in <head>.
- If no items match a topic, show a muted "nothing relevant today" line for that topic.
- An item can appear under multiple topics if relevant to both.
- If a transcript is in German, summarise in English.
- Do not invent information not present in the content.

HTML structure to follow exactly:

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
    .toc ul li a {{ font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:700; color:#4a6fa5; text-decoration:none; }}
    .toc ul li a:hover {{ text-decoration:underline; }}
    .toc ul li span {{ font-family:Helvetica,Arial,sans-serif; font-size:12px; color:#666; display:block; margin-top:2px; }}
    .topic-label {{ font-family:Helvetica,Arial,sans-serif; font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#fff; background:#4a6fa5; display:inline-block; padding:4px 10px; border-radius:3px; margin-bottom:20px; }}
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
      <p>[Full date, e.g. Monday, March 23, 2026]</p>
    </div>
    <div class="body">

      <!-- TABLE OF CONTENTS: one row per topic -->
      <div class="toc">
        <h3>Today's Topics</h3>
        <ul>
          [For each topic:]
          <li>
            <a href="#topic-[slug]">[Topic Name]</a>
            <span>[One sentence: what was found today. E.g. "3 articles on new model releases and chip infrastructure." or "Nothing relevant today."]</span>
          </li>
        </ul>
      </div>

      <!-- TOPIC SECTIONS -->
      [For each topic, give it an id matching the TOC anchor:]
      <div id="topic-[slug]">
        <div class="topic-label">[Topic Name]</div>

        [For each relevant item:]
        <div class="item">
          <h2>[Title]</h2>
          <div class="meta">[source_name] &nbsp;|&nbsp; <a href="[url]">[domain only]</a></div>
          <p>[1 sentence: the single most important fact. Name specific people, companies, tools, or numbers.]</p>
          <ul>
            <li><strong>[label]:</strong> [specific detail with evidence or implication]</li>
            <li><strong>[label]:</strong> [specific detail with evidence or implication]</li>
          </ul>
        </div>

        [If nothing relevant:]
        <p class="nothing">Nothing relevant today.</p>

        <!-- Back to top link at end of each topic section -->
        <a href="#top" class="back-to-top">↑ Back to top</a>
      </div>

      [Separate topics with:] <hr class="divider"/>

      [After all topics:]
      <div class="sources">
        <h3>Sources Checked</h3>
        <ul>
          [For each source:] <li><strong>[source_name]:</strong> [N] checked, [M] included</li>
        </ul>
      </div>

    </div>
    <div class="footer">Daily Digest &nbsp;&bull;&nbsp; [date] &nbsp;&bull;&nbsp; [total N] items reviewed</div>
  </div>
</body>
</html>

Items:
{items_json}
