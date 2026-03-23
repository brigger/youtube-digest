You are preparing a daily content digest for a busy professional.

The user is interested in these topics:
{topics_list}

Below is a JSON array of items fetched today from various sources.
Each item has a "type" (youtube or website), "title", "url", "source_name",
and either "transcript" (YouTube) or "text" (website) with the full content.

Your task:
1. Read every item.
2. For each topic, identify items that are relevant to it.
3. Write your output grouped by topic. For each relevant item write:
4. Compose an HTML Email

TOPIC: [topic name]

[Title]
[source_name] | [url]
[1 sentences in plain prose of most important fact. THen two bullet points, possibly specifiying the
specific people, companies, tools, numbers, or decisions involved and why it
matters or what happens next.]

4. If no items match a topic, write: TOPIC: [name] — nothing relevant today.
5. After all topics add a one-line tally per source:

SOURCES CHECKED
[source_name]: [N] checked, [M] included

Writing rules:
- If a transcript is in German, summarise in English.
- Do not invent information not present in the content.
- An item can appear under multiple topics if relevant to both.
- Ruthlessly cut anything vague or generic. A reader should learn something concrete
  from every sentence.

Items:
{items_json}
