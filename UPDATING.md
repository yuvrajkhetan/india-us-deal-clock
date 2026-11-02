# How the daily update works

These are the standing instructions for the scheduled daily update of the India–US Trade Deal Clock. The scheduled task only points here, so changing this file changes how every future update runs.

The clock lives in two places, and both get the same update:

- **Live site:** this repo (`yuvrajkhetan/india-us-deal-clock`). GitHub Pages serves `index.html` from `main` at https://yuvrajkhetan.github.io/india-us-deal-clock/. The owner has authorised the update to commit and push data updates to `main`.
- **Claude artifact:** https://claude.ai/artifact/51F4z3LDJLMLLi7cGQ5MWY

## What the clock measures

How close India and the US are to formally **signing** the first tranche (interim agreement) of their Bilateral Trade Agreement. It is shown Doomsday-style as minutes to midnight (estimate 0% = 60 minutes, 100% = midnight = signing), plus the chance of signing within 30, 60 and 90 days.

Every number is computed by the page's script from one JSON block in `index.html`: `<script type="application/json" id="model">`. The update only changes that JSON block, then regenerates the share image and pre-rendered content. Do not change the page design, weights, calibration, intent settings or scoring code.

## Source policy

The owner's instruction: rely predominantly on primary or tier 1 sources, so the information is both complete and trustworthy.

- **Primary (best):** official government pages and documents: pib.gov.in, mea.gov.in, commerce.gov.in, pmindia.gov.in, whitehouse.gov, ustr.gov, state.gov, commerce.gov, trade.gov, treasury.gov, federalregister.gov, congress.gov, supremecourt.gov, and other .gov, .gov.in or .nic.in sites; parliamentary answers (sansad.in); officials' verified social media posts.
- **Tier 1 secondary:** Reuters, AP, AFP, Bloomberg (including Bloomberg Government), Financial Times, Wall Street Journal, New York Times, Washington Post, BBC, Politico, CNBC, The Economist, Nikkei Asia; PTI, The Hindu, BusinessLine, Indian Express, Hindustan Times, Times of India, Economic Times, Mint, Business Standard, NDTV, AIR News (newsonair.gov.in), DD News.
- For an official statement, action, document or date, link the **primary** source when one exists; otherwise the tier 1 report.
- Use any other outlet only if no primary or tier 1 source covers the item **and** it is an official's on-record statement quoted directly. Never use another outlet as the only basis for an obstacle, stage, target or key event.
- Never use aggregators, blogs, brokerage or market-tips sites, law-firm or consultancy notes, or outlets re-reporting second hand.
- **Completeness:** search these sources systematically (WebSearch with `allowed_domains` set to groups of the domains above, plus the official press-release pages on both sides), not just a general web search. Check the official readouts of any meeting or call you add.
- Never invent or guess a URL. Only use URLs seen in search results or fetched pages.

## Steps

1. Attach and clone this repo (owner `yuvrajkhetan`, repo `india-us-deal-clock`, push access). Open `index.html`, find the model JSON and note its `asOf` date. If `asOf` is already today's date (India time) on `origin/main`, today's update has already run: stop and say so.
2. Research news from `asOf` to today, following the source policy. Topics: the India-US trade deal and BTA first tranche; statements by Goyal, the Commerce Secretary, Jaishankar, Modi, Trump, Greer/USTR, Rubio, the White House and the US Ambassador; US tariffs on India; Section 301 cases involving India; Russian oil and India-US relations; negotiating rounds. Use only dated reports. Do not re-add inputs already in the JSON.
3. Add new inputs following these rules exactly. Three factors: Progress (stages), Obstacles (blockers), and Intent (built automatically from signals, engagements and missed targets).
   - **signals:** on-record statements by leaders, ministers, negotiators or officials about the deal. Score each statement **at face value**; do not second-guess tactics or audience. −2 hostile, −1 negative/cautious/conditional, +1 positive, +2 "very close"/closing/signing announced. Use 0 only for truly neutral or evenly mixed statements. A postponed or cancelled negotiating round is also recorded here with score −1. Use the official's own words, not a journalist's paraphrase. Fields: `date`, `who`, `score`, `text` (short; quotes under 15 words), `src`.
   - **engagements:** formal negotiating rounds, ministerial meetings on the deal, leaders' calls or meetings (each counts +1). Fields: `date` (last day), `label`, `src`.
   - **targets:** any new official target date for signing. Fields: `set`, `due`, `label`, `src`. A missed target counts −2 automatically the day after it passes.
   - **blockers** (obstacles): new live obstacles with a start date; set `end` when resolved. Severity: 40 if either side suspends talks; 25 for a punitive measure, a dated threat, or the legal basis of the deal being struck down; 15 for a core unresolved issue or a legal/policy review still pending (e.g. tariff law in flux, a pending US investigation); 5 for a side irritant. Name policy items "Policy uncertainty: ...". Fields: `name`, `severity`, `start`, `end`, `src`.
   - **stages:** append only if the stage moves up the ladder (95 signing date fixed, 100 signed). If the first tranche is formally signed, set `signed` to the signing date and add a stage with score 100.
   - **keyEvents:** add only for a genuinely major turning point (title of 1-4 words, one-sentence text, `src`). Keep the list lean.
4. Set `asOf` to today's date (YYYY-MM-DD, India time). Check the JSON is valid and contains no `</` sequences (escape as `<\/`). No em dashes in any text.
5. From the repo root run `python3 scripts/build_share.py`. It renders `og.png` (the 1200×630 link-preview card), rewrites the share tags, and bakes the computed page content into `index.html` for crawlers. Open `og.png` and check the number and date look right.
6. Commit `index.html`, `og.png` and `sitemap.xml` with a message like "Daily data update, <date>" and push to `main`. If the push is rejected because `main` moved, pull with rebase and check step 1 again before retrying.
7. Republish the artifact: read it (Artifact tool, action "read", URL above), replace only its JSON block with the same updated JSON, and publish to the same URL (no icon).
8. Write a 2-3 line summary for the owner: new estimate, minutes to midnight and chances, and the main inputs added with their sources. If nothing new happened, still update `asOf` in both places, rerun step 5, push, and say "No new inputs today". If any input had to rely on a source outside the primary and tier 1 lists, name it. If the repo push or step 5 fails, still update the artifact and say plainly what was not updated and why.

## Formulas (for the summary)

- Intent = 50 + 25 × Σ(w·v) / (Σw + 3), over all events up to today, where v is the event score and w = 0.5^(age in days / 30)
- Estimate = 50% Progress + 30% Obstacles + 20% Intent
- Minutes to midnight = 60 × (100% − Estimate)
- 90-day chance = 1 / (1 + exp(−(Estimate − 70) / 6)); 30- and 60-day chance = 1 − (1 − p90)^(days / 90)

Style: plain language, no em dashes.
