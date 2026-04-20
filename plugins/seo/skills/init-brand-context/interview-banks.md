# Interview Banks — init-brand-context

Gap-closing questions for Phase 8. Organized by file × dimension × specific
gap. One question at a time. Select the highest-impact question for the
lowest-scoring dimension of the file with the largest gap below 90%.

**Hard cap:** 10 questions total across all files. Not 10 per file.
Scrape-first skills should not grind the user through a 30-question
interview. If gaps remain after 10 questions, flag them and write files
at current confidence level.

---

## Selection algorithm

```
while interview_count < 10:
    target_file = argmin(file.confidence) where file.confidence < 90
    if target_file is None: break

    target_dimension = argmin(target_file.dimensions) where dimension_score < ceiling
    specific_gap = pick the highest-impact unanswered gap for
                   (target_file, target_dimension)

    ask(specific_gap.question)
    record(answer, source_tag=CLIENT_VOICE, weight=1.0)
    rescore(target_file)
    interview_count += 1

    if user says "stop" or "good enough": break
    if user says "skip" or "don't know":
        mark gap as [UNKNOWN] and continue loop
```

**Rules:**
- Never ask about something the scrape already answered.
- Never repeat a question.
- If follow-up to the current answer closes a bigger gap than moving
  to the next dimension, ask the follow-up.
- Do not re-sort the question bank — it is already ordered by impact.

---

## Questions per file

Each block lists questions by dimension, ordered by expected confidence
lift per question.

---

### `company.md`

Only interviewed if a field is `[UNKNOWN]` or ambiguous after scrape.
Typically 0–2 questions max.

**Essential coverage**
1. *Name ambiguous (Impressum says X, homepage says Y):*
   "Impressum shows `[X]`, homepage uses `[Y]`. Which one should I write as the
   canonical name?"

2. *Market ambiguous (Impressum DE but English copy + US customers):*
   "Your Impressum is German but the site is English-first with US case
   studies. Which is the primary market for SEO and positioning: Germany,
   US, or somewhere else?"

3. *Language ambiguous (mixed de/en across pages):*
   "The site mixes German and English. What is the primary content
   language you publish in?"

4. *Description missing or >60 words:*
   "One or two sentences — what does the company do, and for whom?"

---

### `competitors.json`

Typically 1–3 questions if the user is engaged. Skip if user confirmed
candidates and the lean scrape is acceptable.

**Essential coverage**
1. *Fewer than 2 competitors confirmed:*
   "I wasn't able to surface strong competitors via search. Who do you
   actually lose deals to or get compared against?"

2. *Observable weaknesses thin for a competitor:*
   "What's something about `[competitor]` that's NOT on their website but
   that you know from dealing with them?"

**Data grounding**
3. *Pricing_visible flagged but unclear:*
   "Does `[competitor]` publish pricing anywhere, or is it always
   on-request? I couldn't tell from their site."

**Consistency**
4. *Positioning tension between client's view and scraped copy:*
   "Their homepage says `[X]`, but you might have a different read. How
   would you actually describe `[competitor]`'s positioning in one line?"

---

### `icp.md`

Typically 3–5 questions. This is where interview delivers the most lift,
because disqualifiers and decision process are rarely in marketing copy.

**Essential coverage**
1. *Disqualifiers missing (almost always the biggest gap):*
   "Who do you deliberately NOT serve? What kinds of prospects do you
   turn down or would rather not work with?"

2. *Situational triggers weak:*
   "What's usually happening at the customer's company right before they
   reach out to you? Funding round, leadership change, compliance
   deadline, something else?"

3. *Decision process incomplete:*
   "Who actually signs off on buying this? One exec, a committee,
   evaluation team, procurement? And who influences the decision even
   if they don't sign?"

4. *Must-haves missing:*
   "What does a prospect need to already have in place for your offering
   to be a fit? Team size, tech stack, compliance requirements,
   something else?"

**Data grounding**
5. *No metrics present:*
   "Can you give me a typical customer size or revenue range? Rough is
   fine."

**Consistency**
6. *Multiple industries named on site without hierarchy:*
   "Your site mentions `[industries A, B, C]`. What percentage of revenue
   comes from each, roughly? Is one of these primary and the others
   opportunistic?"

---

### `personas.md`

Typically 3–5 questions. Search behavior and vocabulary are interview-only.

**Essential coverage**
1. *Search behavior missing (default for almost every scrape):*
   "When your best prospects are looking for a solution like yours, what
   do they actually type into Google? Give me 3 phrases if you can."

2. *Vocabulary sparse:*
   "Can you share 3 phrases your best customers use when they describe
   their problem to you? Their actual words, not yours."

3. *Objections missing:*
   "What are the top 2 objections prospects raise before they buy? The
   real ones, not the polite ones."

4. *Background missing:*
   "Typical professional background of your primary buyer. What were they
   doing before this role? What's their domain of expertise?"

5. *Second persona missing (only one buyer type identified):*
   "Is there a second persona who also buys from you, or influences the
   buying decision? Different role, different priorities?"

**Data grounding**
6. *No named roles from scrape:*
   "What's the exact job title of your primary buyer? Not the category,
   the actual title on their LinkedIn."

**Voice / tone**
7. *Voice/tone notes thin:*
   "How does your primary buyer communicate in sales calls — formal or
   casual? Technical detail or big picture? Quick decisions or long
   evaluation? Pick the closest pattern."

---

## Question style rules

- **One question at a time.** Never stack.
- **Closed where possible.** Prefer forced-choice ("A, B, or C?") over
  open-ended ("tell me about your buyers"). Open-ended burns budget.
- **Concrete asks.** "Give me 3 phrases" beats "describe their vocabulary."
- **No assumptions about domain.** Do not ask "how do your enterprise
  buyers differ from your SMB buyers" unless both segments are already
  confirmed.
- **Respect "skip" and "stop".** Mark unknowns, move on, or end loop.
- **Honor the cap.** At question 10, stop and move to Phase 9 regardless.
