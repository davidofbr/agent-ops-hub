# Extraction Fields — What to Pull From Every Page

This is what content-dissector extracts from each of the top 10 pages.
Every field has a reason. If you find yourself tempted to skip one,
re-read why it's here.

## Fields and rationale

### page_title
The actual `<title>` tag content as Jina rendered it. Downstream AI
needs this to see how competitors frame the query — the title is the
first positioning decision.

### meta_description
Same reason. Also shows what the page *claims* to cover vs what it
actually covers (the delta is often revealing).

### domain
For the citation map and coverage analysis. Strip scheme and path,
keep only the host. Subdomains count as separate domains
(blog.hubspot.com ≠ hubspot.com for citation purposes).

### content_length_words
Count of the main content body. Not a target, not a recommendation —
a signal. Use it to spot outliers (the one 500-word page in a top 10
of 3000-word pages is doing something different).

Exclude navigation, footer, cookie banners, sidebars. Use judgment.

### h_outline
All H2/H3 headings in order. This is the argument structure of the
page. Downstream AI uses this to see how competitors organize the
topic — and where they don't.

Don't include H1 (it's usually the title). Don't include H4+ (noise).

### main_points
A compressed walk through the page top to bottom. One bullet per
section or logical unit. Describe what each section *argues or
claims*, not what it's titled.

Bad: "Section about pricing"
Good: "Argues that pricing should be transparent, gives three examples of SaaS companies that publish tier details"

This is the field downstream AI uses to understand each page's actual
content, so it has to be substantive. 6–15 bullets per page is normal.

### entities
Named things the page covers. People, companies, products, frameworks,
stats, tools, concepts. This powers the coverage map — the entity
overlap across top 10 is what tells us table-stakes vs gaps.

Be specific: "HubSpot", "Marketing Cloud", "42% open rate", "Dr. Maren
Becker", not "a CRM" or "a statistic".

### questions_answered
What specific questions does this page answer? 3–8 per page. Phrase
them as the reader would ask them.

Good: "How much does marketing automation cost for a 50-person company?"
Bad: "Pricing"

### images_count
Rough count. Signal for visual-heavy content strategies.

### has_original_data
Boolean. Did this page produce its own data — a survey, a study, a
benchmark, a case study with real numbers — or is it recycling?
Original data is an E-E-A-T signal and a competitive moat.

### has_author_byline
Boolean. Is there a named human author with credentials or bio link?
Another E-E-A-T signal, especially important for YMYL topics and for
AEO (Google's AI Overview favors pages with clear authorship).

### publish_date / last_updated
When was this published and when was it last touched? Freshness matters
for most commercial queries. Null if not visible on the page.

### ctas
Commercial intent is in the CTAs. Extract:
- `primary`: the main call-to-action verb phrase ("Demo buchen", "Kostenlos testen")
- `primary_placement`: where it appears ("hero", "sticky header", "after H2 blocks", "footer")
- `primary_count`: how many times the primary CTA appears on the page
- `secondary`: the second most prominent CTA
- `secondary_count`: how many times

Why: CTA strategy reveals funnel position. A page with one primary CTA
at the bottom is top-of-funnel content. A page with sticky header +
three in-body + footer is bottom-of-funnel.

For content pages with no CTAs (Wikipedia, editorial), set all fields
to null.

### schema_types_detected
Structured data types visible in the markdown or inferrable from the
page structure. Article, FAQPage, HowTo, Product, Review, Organization,
BreadcrumbList, VideoObject. List what you see.

Jina's markdown output won't always surface schema cleanly. If you
can't tell, set to empty array — don't guess.

### notes
Free-form field for anything a strategist would flag. Examples:
- "Clearly outranks peers on freshness — updated last week"
- "Thin content disguised as long with filler sections"
- "Appears to be LLM-generated, no original angle"
- "Uses proprietary framework they've branded"

One or two sentences max. Keep it useful, not chatty.

## What NOT to extract

- Internal link counts (not useful without full crawl)
- External link counts (same)
- Exact HTML markup (Jina strips it — don't try to reconstruct)
- Screenshots (out of scope, different tool)
- Backlinks / DR / DA (v1 scope excludes authority scoring)
- Load time / Core Web Vitals (different tool)
