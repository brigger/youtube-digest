You are generating one section of a daily content digest email for a busy professional.

Topic: {topic_name}
Topic ID (use exactly for HTML anchors): {topic_slug}
Show up to {topic_count} items for this topic.

Below is a JSON array of items from various sources (YouTube and websites).
Each item has "type", "title", "url", "source_name", and "text" or "transcript".

Rules:
- Find items relevant to this topic. If none, say so.
- An item counts as relevant if it meaningfully relates to the topic.
- Keep summaries in the original language of the source — do not translate.
- Do not invent information not present in the content.

The output has two parts — a TOC entry and a detail section:
- TOC entry: lists item titles with ~200-character one-sentence summaries, each linking to the detail below.
- Detail section: one key sentence per item plus two specific bullet points with names, numbers, or outcomes.

Output EXACTLY the following format — nothing before ===TOC=== and nothing after the section HTML:

===TOC===
<li>
  <a href="#topic-{topic_slug}">{topic_name}</a>
  [If items found, add:]
  <ul class="toc-items">
    [For each item numbered from 1:]
    <li><a href="#item-{topic_slug}-[n]">[Title]</a> — [~200-char summary: one crisp sentence with specific names, numbers, or outcomes]</li>
  </ul>
  [If nothing relevant instead:] <span>Nothing relevant today.</span>
</li>
===SECTION===
<div id="topic-{topic_slug}">
  <div class="topic-label">{topic_name}</div>
  [For each item (numbered from 1, matching TOC):]
  <div class="item" id="item-{topic_slug}-[n]">
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
  <a href="#top" class="back-to-top">↑ Back to top</a>
</div>

Items:
{items_json}
