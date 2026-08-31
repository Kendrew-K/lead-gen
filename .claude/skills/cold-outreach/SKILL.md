---
name: cold-outreach
description: >-
  How to write cold outreach that gets replies: campaign mode, reading enrichment into a
  real diagnosis, hook selection, offer framing, CTA choice, follow-up sequences, and the
  metrics that tell you which part is broken. Use EVERY time you draft a WhatsApp message
  or email for this Lead Gen tool (the drafts.json step), and any other time you write a
  cold message to a stranger. Technique is product-agnostic; the worked examples are
  Indonesian B2B lead gen.
---

# Cold Outreach

Sources: Coursera, "How to Write a Cold Outreach Email" (structure, 30/30/50 rule,
follow-up cadence, tracking). Coursera, "Digital Marketing Explained in 5 Minutes"
(channel taxonomy only — the video is career guidance and contains no outreach
technique). `gtmagents/gtm-agents` (cold-email-personalization, MIT).
`growthenginenowoslawski/coldoutboundskills` (poke-the-bear + billboard patterns, built
from 1,000+ campaigns). `borghei/Claude-Skills` (follow-up angle rotation).

This file is about **technique**. The Indonesian lead-gen examples are illustration, not
the point. Swap the product, the method holds.

## Where the result actually comes from

The 30/30/50 rule. Effort spent on the wrong third is wasted:

| Share | Lever | If replies are near zero, suspect |
|---|---|---|
| 30% | Picking the right targets | You are writing beautifully to people who cannot buy |
| 30% | The message itself | Hook, offer, CTA |
| 50% | **Follow-up** | You sent once and stopped |

Follow-ups are roughly **twice** as likely to get a response as the first touch. A
campaign with no follow-up sequence is a half-built campaign, no matter how good the
first email is. Never write a first touch without writing its follow-ups in the same
sitting — see "Follow-up sequence" below.

---

## Step 1: the mode

Before anything else, read `mode` from the campaign file. It decides who you target,
what proof matters, and what you are allowed to ask for. **The same business gets a
completely different message in a different mode.**

| Mode | You want | Target is | Proof that matters | CTA shape | Fatal mistake |
|---|---|---|---|---|---|
| `new-customer` | They buy your service | The budget holder | A result you produced | Free bounded artifact, or a call with its own payload | Pitching before they know why you're relevant |
| `partnership` | Mutual referral or co-delivery | A **peer serving your buyer**, never a competitor | Deal flow you can send them — or, with none yet, a concrete structure you're proposing | "Swap" framing: a short chat between equals | Reading as a disguised sales pitch. Partnership emails that pitch get ignored twice. With zero proof, **propose the arrangement — never imply existing clients** |
| `supplier` | You buy from them | A vendor with capacity | That you are a serious, funded buyer | Ask for pricing / capacity / lead time | Being vague about volume. They quote fast when the job is real |
| `validate` | Information, nothing else | Anyone in the segment | None. You are the one asking a favour | **One** opinion question, answerable in a word | Selling anyway. Or asking for operational data a stranger has no reason to give you |

Mode rules that are easy to get wrong:

- **`partnership` leads with what you bring, not what you do.** "Saya lagi ada beberapa
  klien yang nyari X, kalian ngerjain itu?" outperforms any description of your company.
  You are proposing a trade, so the first sentence has to contain your side of it.
- **`validate` must promise no pitch, and then actually not pitch.** One sentence:
  `Saya nggak jualan apa-apa, lagi riset.` If you sell in a validate campaign, delete the
  mode from the project, because you'll never be able to run it honestly again.
- **`validate` is the lowest-yield mode here, and the reason is not busyness.** An owner
  who ignores your questions is usually not too busy — they're wondering why a stranger
  wants to know how their business runs. So:
  - **Ask for an opinion, never for operations.** `Klien terakhir dateng dari mana?` is
    commercially sensitive and reads like a competitor scouting. `Menurut kalian, klien
    interior sekarang lebih milih lewat Instagram atau rekomendasi?` costs nothing to
    answer and lets them be the expert, which people enjoy being.
  - **One question. Answerable in one word.** Not two, not a list. The bar is a reply
    they can thumb out at a traffic light.
  - **WhatsApp, not email.** Email is where Indonesian SME owners handle invoices and
    formal matters, so an unsolicited question there feels like work. WhatsApp is
    conversational and gets one-line replies all day.
  - Expect a low answer rate regardless, and treat every reply as a gift. If you need
    volume of insight, `supplier` and `new-customer` replies teach you more per message.
- **`supplier` is the easiest mode and the one people skip.** You are offering money.
  Reply rates run far above the others. Be concrete about volume and timeline.
- Mode also changes **who you search for**. A `partnership` campaign targeting interior
  designers is not the same Places query as a `new-customer` one. Check that
  `categories` in the campaign file actually matches the mode before drafting.

---

## Step 2: read the research before writing a word

Every lead in `leads.json` carries a `research` block: `rating`, `reviews_count`,
`review_quotes` (up to 5, with `when`), `summary`, `hours`, and `site`
(`title`, `description`, `headings`, `socials`, `has_form`, `since`, `reachable`).

**Do not go looking for complaints.** In this segment Google reviews are near-uniformly
5-star. That is not a dead end — it is the finding. The signal is in the *shape* of the
data, not the sentiment:

| What you see | What it means | Hook it supports |
|---|---|---|
| High rating + high review count + **newest review is years old** | Delivery is proven. Demand has gone quiet. | The strongest hook available. Compliment is true, gap is true, and it is exactly the thing you fix. |
| All 5 reviews clustered in the last 2 months | New listing, or an active push right now. They are moving. | Timeline hook. Speed and volume, not "you need clients". |
| 1-5 reviews total, all recent | Brand new. No reputation yet. | They need proof, not volume. Different offer. |
| Reviews describe the **office**, not the work | People are reviewing a place they visited, so walk-ins/visits are a channel | Specific, flattering, verifiable observation |
| Only channel is Instagram / a contact form | Inbound-only. No outbound exists. | "You're missing a channel", the safest frame there is |
| No website at all, recent reviews | Running on WhatsApp and word of mouth | Do not condescend. They may be doing fine. Goal question. |
| `since` present, e.g. "sejak 2010" | Longevity. Do the arithmetic and use it. | Credibility, and a real timeline anchor |
| Site headings list many service lines | Segments with different buyers, one funnel | "Who chases each line?" — the segmentation poke |
| Rating below ~4.7 with volume | Real friction somewhere | Handle with care. Never state it. At most, ask. |
| `Tbk` / very large / tender-driven / only a generic `info@` | **Nobody who can say yes will ever read it** | **Do not message. Drop the lead.** |

**The reputation-versus-distribution gap is the workhorse of this project.** Formally:

> Rating is high, review count is high, the newest review is old, and there is exactly
> one channel. Therefore the work is good and the pipeline is not.

It is safe because the first clause is a compliment, and honest because every clause is
sourced from data you actually fetched. Use it whenever the shape fits.

### Disqualify before you write

Not every lead the tool returns should be messaged. Writing a good email to the wrong
company is the 30% of effort that produces nothing. Drop a lead outright when:

- **The buyer is unreachable.** A `Tbk`, a large tender-driven firm, or anything where
  the only address is `info@` and the decision sits three floors up. Your message reaches
  an inbox nobody who can say yes is reading.
- **Buying is procedural, not discretionary.** If they acquire vendors through tender or
  procurement, a cold email cannot enter that process and pretending otherwise wastes
  everyone's time.
- **They already do what you'd be offering**, in-house and visibly.
- **The listing is a branch of a lead you already have.** Same inbox, two Google pins.

Dropping leads is cheap. Being remembered as the person who cold-emailed a public company
asking for an internal contact is not.

### Never ask a stranger for someone else's contact

`Boleh diarahkan ke siapa yang pegang X?` is banned. Asking a company you have no
relationship with to hand over an internal person's name or number reads as prospecting
for a list, and it is the fastest way to be marked as a nuisance by the one human who
did open your email.

The legitimate version is to make it trivially forwardable and let *them* decide:
`Kalau ini lebih pas buat orang lain di tim kalian, silakan diteruskan.` One line, no ask,
no obligation. If a lead only works via a referral you have to request, the real answer
is that it was the wrong lead — see the disqualify list above.

### Rules for using research
- **Every claim must be traceable to a field you actually read.** If you cannot point at
  the value in `research`, cut the sentence. An invented specific is worse than a generic.
- **Never quote a review back at them.** It reads like surveillance. Use what the review
  *told you*, not its words.
- **Never mention the rating number.** "Rating 5.0 dari 93 ulasan" reads scraped, because
  it was. Say what it implies instead.
- **Absence is evidence.** No LinkedIn, no site, no recent reviews — all usable, all true.
- One finding per message. You will often have three. Pick the one the offer answers.

---

## Step 3: hook type

Ranked. Use the highest one your information supports.

### A. Billboard (offer-first) — default when research came back thin

State what you do and what you're offering, immediately. No diagnosis, no guessing at
their pain. Self-selecting: only interested people reply, and that's the point.

Open with a **goal question**, not a pain question. Ask about the ambition, not the wound.

> `Lagi pengen nambah klien baru di luar iklan sama referral?`

Needs zero research, cannot insult anyone, cannot invent a false fact. When the research
block is empty, this is the correct choice — not a fallback.

Cap the goal question at **two options**. A menu dilutes. If you use two, make the second
one your differentiator.

### B. Diagnosis — when the research shape is clear

The reputation/distribution gap, or any other sourced pattern from the table above.
Structure: **true compliment → the gap it implies → question.** The compliment is what
makes the gap survivable.

> `Kerjaan kalian jelas bagus, ulasannya konsisten bertahun-tahun. Yang agak sepi
> justru yang baru, ulasan terakhir udah lama. Emang lagi fokus ke proyek lama, atau
> yang baru lagi seret?`

This is the highest-converting hook in this project because it is specific, flattering,
and impossible to send to a random business.

### C. Poke the bear — when you know the category but not this lead

Ask about their current process in a way they can't confidently answer yes to. They find
the gap themselves. No accusation, and it earns a reply because it's a real question.

- Classic: `Udah ada cara yang bisa diandelin belum buat [outcome]?`
- Status pressure: `[Task] masih manual, atau udah ada sistemnya?`
- Soft humility: `Mungkin saya salah, tapi kayaknya belum ada yang pegang [area] ya?`
- Leverage: `Gimana caranya [outcome] tanpa nambah orang?`

The leverage variant is strong for small businesses: capability without headcount is
money and risk at once.

### D. Timeline — when a real dated trigger exists

Reference a specific event, deadline, or seasonal window in their world. Converts to
meetings ~3.4x better than problem hooks, but **only with a genuine trigger**. Invented
urgency is worse than no hook.

> `September-Oktober perusahaan mulai susun budget tahun depan.`

Valid: hiring posts, new location, new service line, budget season, regulatory dates,
review clustering that shows a current push, their own published dates. Not valid:
funding announcements (scraped to death), LinkedIn posts (everyone assumes you scraped).

### E. Problem hook — weakest, use last

Assert a pain and ask them to confirm. ~4.4% reply vs ~10% for timeline. Two failure
modes: you guess wrong and lose them, or you guess right but describe exactly the gap
your product fills, which reads as pitch wearing an observation costume.

If you use it: name **what the gap costs**, not the gap. Not "kurang klien" but "tukang
nganggur tapi tetap digaji." Concrete scene over abstraction. One pain, never three.

### Hook rules, all types
- Question they'd nod at, never an accusation. `Bisnis kalian pasti lagi susah` is banned.
- Never invent a fact you can't verify from the lead data.
- One idea per message.
- If a random person could say it about any business, cut it.
- Vary the type across a list. Eighteen leads with the same hook is a template smell, and
  two of them may know each other.

---

## Step 4: CTA — pick by production prerequisite

The rule most people get wrong. **The best CTA is giving them the thing. Whether you can
depends entirely on how much of their input the deliverable needs.**

Ask: *can I produce something useful with only public information?*

| Their input needed | CTA shape | Example |
|---|---|---|
| **None** — public info is enough | Offer the artifact. Meeting comes after. | `Mau saya kirimin?` |
| **Some** — you can guess and be roughly right | Offer a sample built on assumptions, meeting is to correct it | `Saya udah bikin versi tebakan. Kalau meleset, 15 menit ngobrol saya benerin.` |
| **Deep** — cannot start without discovery | The meeting *is* the deliverable. Make it valuable on its own. | `15 menit, kita petain target market kalian bareng. Hasilnya kalian simpan, mau lanjut atau nggak.` |

"I'll do it free, want it?" beats "can I have 15 minutes?" every time — accepting a free
artifact costs nothing, booking a meeting costs calendar space and a decision. But you
cannot promise an artifact you're not able to build yet. Lead gen is the middle-to-deep
case: without knowing their target market and product, sourcing the right prospects is
impossible. So sell the meeting, but give the meeting its own payload.

Never let the deep case degrade into "can I show you a presentation?" If the meeting is
the offer, the meeting must produce something they keep.

### CTA rules
- **Repliable in five words or fewer.** If not, simplify.
- One CTA. Never two.
- **Ask for 10 minutes, not 15.** Ten reads as a favour, fifteen reads as a meeting.
- **Attach availability to any meeting CTA**, and make it their-side flexible:
  `Senin sampai Jumat saya ikut jadwal kalian.` One short line. It removes the
  back-and-forth that kills a yes, and it signals you'll travel to them.
  Attach it **only to meeting CTAs** — on an artifact CTA (`Mau saya kirimin?`) there is
  no meeting to schedule, and adding it just dilutes a clean four-word ask.
- Confirmation CTAs work when you asserted something: `Masih gitu nggak sekarang?`
- Qualifying CTAs are efficient: `Ada rencana lini baru nggak tahun ini?` — the answer
  either advances or kills the lead instantly.

### Free offers
- **Bound it.** "20 calon klien gratis" is credible; "saya kerjain gratis dulu" reads
  scammy or devalues you. An edge makes it real.
- **Cap it**, and say the cap, if the cap is true.
- Only promise free work you can deliver at the volume you're sending. Six yeses out of
  eighteen is a real week of unpaid work.

---

## Message construction

### Skeleton — three beats, both channels

```
[Hook: diagnosis, goal question, poke, or trigger — one line]
[Who you are + what you do: identity line, then mechanism + contrast. 2 sentences.]
[Offer + CTA: the free thing, then the five-word ask.]
```

### The identity line

A cold message from a nameless entity is easy to delete. One line of human identity makes
it a message from a person, and people answer people. This is not the same as a company
introduction, which stays banned.

| Banned: credential intro | Required: identity anchor |
|---|---|
| `Perkenalkan, kami adalah perusahaan yang bergerak di bidang...` | `Saya Kendrew, orang Jakarta juga.` |
| Company voice, plural, about capabilities | First person singular, about a human |
| Opens the message | Comes **after** the hook, never before |
| Credentials, years, client counts | Where you are, what you're doing, why them |

Rules:

- **Never open with it.** The hook opens. An intro in line one wastes the preview text and
  reads as a template, which is exactly what you're trying not to be.
- **One line. Twelve words or fewer.** It's an anchor, not a bio.
- **Say "saya", never "kami"**, unless a team genuinely exists. Plural self-reference reads
  as a company hiding, and under the zero-proof rule it's a fabrication.
- **Anchor on something human and checkable**, not on qualifications: your city, that
  you're new at this, what drew you to their trade. Vague is fine. False is not.
- **Best version ties you to them.** `Kalian salah satu yang pertama saya hubungin` is
  personal, flattering, and honest early in a campaign. Only use it while it's true.
- It merges into beat 2 rather than adding a beat, so the word count doesn't move.

Working shapes:

> `Saya Kendrew, orang Jakarta juga, lagi bangun layanan outreach buat usaha interior di sini.`

> `Saya Kendrew. Baru mulai kerjain ini, dan kalian salah satu yang pertama saya hubungin.`

On WhatsApp, put the name in the **first** message — an unknown number with no name is
deleted faster than any email. On email the signature carries it, so the identity line can
be shorter.

Contrast matters in beat 2. Say what you are *instead of*: `outreach langsung, bukan
iklan sosmed`. That positions you as a missing channel rather than a competitor to
something they already pay for.

Prefer "you're missing a channel" over "you have a problem." Nobody defends against the
first. Everybody defends against the second.

**Name the channel they actually run.** The standard marketing channels are SEO, content,
email, paid ads (PPC), social, influencer, and affiliate. Everything in this segment is
one of: Google listing (SEO), Instagram/TikTok (social), the occasional endorse
(influencer), and word of mouth. The `research` block tells you which — `socials`,
`has_form`, review volume. Contrast against **the one they have**, by name:

- Instagram-only → `bukan nunggu orang nemu Instagram kalian`
- Google listing + form → `bukan nunggu ada yang isi form`
- Word of mouth only → `mulut ke mulut nggak bisa diatur jadwalnya`

Generic contrast (`bukan iklan`) is weaker than contrast against the specific channel
you can see them running. Outbound is the one channel none of them have, which is why
"missing channel" is true here and not just a framing trick.

### Subject line
- **2-6 words. Under seven, always.** Lowercase. Curiosity or the offer itself.
- Test: could a colleague plausibly send this subject? If yes, good.
- No spam triggers: `gratis` in the subject, `!!`, ALL CAPS, `promo`, `penawaran`.
  (`gratis` in the *body* is fine and often the point. In the subject it filters you.)
- Banned: "quick question", "curious", "following up", the company's own name alone.

### Preview text (the pre-header)

Marketing tools put an insight or statistic in a hidden pre-header. **We send plain
text, so there is no hidden slot** — Gmail's preview is simply the first ~90 characters
of the body, greeting included. That real estate is being spent whether you plan it or
not.

So: **the greeting plus the opening clause must read as a complete, interesting
fragment inside ~90 characters.** Write the first line, then read only the first 90
characters of it and ask whether that alone would earn the click.

- Wastes it: `Halo tim X, Perkenalkan saya Kendrew dan saya bergerak di bidang...`
- Earns it: `Halo tim X, Ulasan kalian bagus semua dan itu nggak gampang buat kitchen set.`

If you ever have a **real, sourced statistic**, this is where it goes. Do not borrow one
and do not invent one — an unsourced number is the fastest way to be read as spam. The
best statistic you will ever have is your own: once `stats` has real numbers, `Dari 40
kontraktor Jakarta yang saya hubungin bulan ini...` beats any figure from an article.

### Social proof, and the zero-proof rule

The standard sales template links a case study: *"how [similar company] did it."* Use
that slot the moment you can fill it honestly. Until then:

| What you have | What goes in the slot |
|---|---|
| Nothing yet | The bounded free offer. It *is* the proof substitute — you are proving it at your own cost instead of claiming it. |
| One finished job | One concrete number and the segment. `Buat satu studio interior di Jakarta, 20 nama jadi 3 yang lanjut.` |
| Several | Pick the closest match to this lead's segment, never the most impressive one. |

Never a logo wall, never "dipercaya banyak klien", never a testimonial you paraphrased.

**Assume zero proof unless the campaign file says otherwise.** Most campaigns here are a
new idea being tested, not an established business. In that state the offer is a
hypothesis and the message has to read like one.

Banned when you have no clients yet — every one of these is a fabrication:

- `klien saya`, `beberapa klien`, `klien kami biasanya` — you have none
- `saya lagi pegang beberapa studio interior` — implies a book of business
- `biasanya hasilnya X` / any rate, conversion, or number from work you haven't done
- `udah kebukti`, `banyak yang cocok`, `metode yang terbukti`
- implied scale: `tim saya`, `kapasitas kami`, anything plural about yourself
- a named similar company, even unnamed-but-identifiable (`satu kontraktor besar di Jakarta`)

What you may say instead, and it works better than people expect:

- **Say you're new, plainly.** `Saya baru mulai kerjain ini` disarms. It converts a
  suspicious pitch into a straight proposal, and it makes the free offer make sense.
- **Describe the method concretely.** Mechanism is not a claim. *How* you would find
  their clients is checkable and specific, and it carries the credibility a case study
  would have carried.
- **Make the free thing the entire proof.** `Saya kasih 20 nama dulu, gratis, kalian
  nilai sendiri` transfers all the risk to you. That is a stronger honest signal than any
  number you could quote.
- **Propose, don't report.** Future and conditional tense throughout: `kalau cocok`,
  `saya bisa`, `mau saya coba dulu`. Never past tense about results.

Being new is a weak card played honestly. A borrowed case study is a strong card that
collapses the moment they ask one question, and in a small market they will ask.

### Length and readability
- **Email body: 50-90 words.** Read aloud; over ~20 seconds, cut.
- **WhatsApp: 2-3 short sentences.** Shorter than the email. One emoji max, usually none.
- Write at roughly an **eighth-grade level**. Short sentences, common words, no clauses
  stacked on clauses.
- **Assume a phone screen.** One idea per paragraph, a blank line between each, nothing
  that needs horizontal reading. A paragraph over four lines on mobile does not get read.

### Them-to-us ratio
Sentences about THEM vs about US. Aim **3 : 1**. All "saya/kami" means rewrite.

### Greeting
`contact_name` present → `Halo Pak/Bu {name},`. Absent → `Halo tim {business},`.
Never guess a name, never guess a gender from a name.

### Banned on sight
- "Semoga pesan ini menemukanmu dalam keadaan baik", "semoga sehat selalu"
- "Perkenalkan, kami adalah...", "Kami ingin menawarkan..."
- em-dashes (they read AI-written and don't fit WhatsApp)
- delve / unlock / elevate / seamless / leverage / sinergi / solusi inovatif
- three-item lists as rhetoric (`cepat, murah, dan berkualitas`), corporate filler, double
  spaces. Enumerating two or three actual questions in `validate` mode is not this — but
  cap it at two, since every extra question lowers the odds of any answer.
- the rating number, a quoted review, any fact not in the lead data

---

## Follow-up sequence

Half the result. Write the whole sequence when you write the first touch — never later,
because later never comes.

Default schedule, measured from the **first send**: **day 3, day 8, day 15.** The tool
threads each one under the original email, so they read as a nudge, not a new pitch.
(Day 3 is aggressive by the article's ~1-week guidance. It suits WhatsApp-paced
Indonesian B2B; if reply rate is fine but stop-outs climb in `stats`, push to day 5.)

**Never resend the same angle.** Rotate:

| Touch | Day | Angle | Shape |
|---|---|---|---|
| 1 | 0 | Your best hook | Full three-beat message |
| 2 | 3 | New evidence, or shrink the ask | Two lines. Add one concrete thing the first email didn't have, or make the ask smaller: `Kalau 20 kebanyakan, saya kirim 5 dulu?` |
| 3 | 8 | Different angle entirely | Reframe for a different motive: cost, speed, a segment you didn't mention |
| 4 | 15 | Close the loop | State plainly that this is the last one and you'll stop. Optionally add `Kalau ini lebih pas buat orang lain di tim kalian, silakan diteruskan.` |

- Follow-ups get **shorter each time**, never longer. Touch 4 is two sentences.
- Never open with "just following up" or "checking in". Lead with the new thing.
- Touch 4 never asks for a name, a number, or an introduction. See "Never ask a stranger
  for someone else's contact".
- Say you're stopping, and stop. `Kalau nggak ada kabar saya nggak akan ganggu lagi.`
  It gets replies on its own and it keeps you honest.
- After a `stop`/`berhenti` reply the tool marks the row `stopped`. Never contact again.

### drafts.json format

One entry per lead, aligned 1:1 with `leads.json`:

```json
{
  "whatsapp": "...",
  "email_subject": "...",
  "email_body": "...",
  "followups": [
    {"days": 3,  "body": "..."},
    {"days": 8,  "body": "..."},
    {"days": 15, "body": "..."}
  ]
}
```

`days` is counted from the first send. Omit `subject` on a follow-up and it threads as
`Re: <original>`, which is what you want. Opt-out line on email only, never WhatsApp.

---

## Metrics

Track **who you contacted, when, and whether they replied** — that is the whole
requirement, and `python run.py stats --campaign <name>` reads it off `outreach.csv`.
Run `sync` before `stats` or the numbers are stale.

| Number | Reads on | If it's bad |
|---|---|---|
| `reply_rate` | The campaign overall | Below ~5%, the problem is usually targeting (the first 30%), not wording |
| `reply_rate_first_touch` vs `replies_after_followup` | Whether the sequence earns its keep | If follow-ups add nothing, your rotation is repeating the first angle |
| `median_reply_hours` | Urgency of the segment | Days, not hours, means plan a longer sequence |
| `stopped` | Whether you are annoying people | Climbing means slow the cadence or fix the targeting |
| `awaiting` | Follow-up debt | If this is large and old, you stopped following up |

**Change one thing at a time.** Subject line or hook type or CTA — never all three, or
the numbers tell you nothing. Sample sizes here are tiny, so treat a difference under
about ten replies as noise and keep sending.

**Send on a weekday morning** for the best open rate. **Reply fast** when someone
answers; speed of reply is the one variable fully under your control.

---

## Before shipping

### Scoring rubric (0-100) — score every email

| Dimension | Pts | Test |
|-----------|-----|------|
| Hook | 25 | Does line 1 earn line 2? Highest hook type the research supports? |
| Value clarity | 25 | Concrete mechanism + contrast, not adjectives? |
| Offer/CTA fit | 20 | CTA matches production prerequisite *and* the mode? Repliable in 5 words? |
| Personalization | 15 | Tied to this lead's research, and every claim traceable to a field? |
| Punchiness | 10 | 50-90 words, mobile-shaped, no fluff? |
| Subject + preview | 5 | Under seven words, lowercase, not salesy? First ~90 chars of body earn the open on their own? |

**>= 85 ship · 70-84 one more pass · < 70 rewrite.**

### The "would I reply?" test
1. Do they see I understand their situation?
2. Is the ask genuinely low-effort?
3. Is there a reason to reply *now*?

Any no → rewrite.

### Batch check
Read all the drafts in one pass, in order. If the same hook type appears three times in
a row, or two messages share a sentence, rewrite. A list that reads as a list is a list.

---

## Worked example (this project: `new-customer`, Indonesian B2B lead gen)

Product needs deep discovery, so the CTA is the middle case: bounded free artifact,
meeting to correct it.

Research for this lead: rating 5.0, 93 reviews, newest review 3 years old, site says
"Our Portfolio on Instagram", contact form present, no other channel.

```
Halo tim Portu Interior,

Ulasan kalian bagus semua dan itu nggak gampang buat kitchen set. Cuma yang
terbaru udah lama, dan dari luar keliatannya klien baru masih ngandelin orang
nemu Instagram kalian sendiri.

Saya kerjain sisi sebaliknya: nyariin orang yang lagi renovasi atau baru pindah
di Jakarta, terus saya hubungin satu per satu. Bukan iklan, bukan nunggu.

Buat mulai saya kasih 20 calon klien dulu, gratis, biar kalian nilai sendiri.

Mau saya kirimin?

Kendrew

Kalau kurang relevan, balas 'stop' saja ya.
```

Mode: `new-customer`. Hook: diagnosis (reputation/distribution gap), every clause sourced
from `research`. Beat 2: mechanism + contrast against the channel they actually run
(Instagram, per `site.headings`). CTA: bounded free artifact, four-word ask — so no
availability line. Preview text lands as `Halo tim Portu Interior, Ulasan kalian bagus
semua dan itu nggak gampang buat kitchen set.` — a complete thought inside the cut.
Note what it does *not* do: no rating number, no quoted review, no claim about their
revenue. Opt-out on email only.
