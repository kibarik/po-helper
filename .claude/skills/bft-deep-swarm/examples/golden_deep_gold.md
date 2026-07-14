# Eval fixture — GOLD (reference = direct-PO quality bar)

Input: `bft-deep-eval-fixture-summary.md`
Purpose: prove swarm BFT quality is NOT worse than direct-PO interaction.

## Two-tier annotated claim table
Each claim a competent PO+analyst would put in the BFT, tagged by tier + anchor + expected swarm behavior.

| # | Claim (belongs in BFT) | Tier | Anchor (source) | Expected swarm behavior |
|---|---|---|---|---|
| C1 | As-Is: возврат = ручная операция оператора, SLA до 3 дней | SOURCE | Summary (Анна) | ground correctly |
| C2 | Problem: 40% тикетов июня = возвраты → нагрузка на поддержку | SOURCE | Summary (отчёт Анны) | ground correctly |
| C3 | BT: пользователь инициирует возврат сам из ЛК подписки | SOURCE | Summary (тема) | ground correctly |
| C4 | Constraint: возврат только в окне 14 дней от оплаты | SOURCE | Summary (Ирина, оферта) | ground correctly |
| C5 | IT: интеграция с refund-API платёжного шлюза | SOURCE | Summary (Олег) | ground correctly |
| C6 | How-to-demo / acceptance: возврат без создания тикета | SOURCE | Summary (Анна) | ground correctly |
| C7 | FT: частичный vs полный возврат — правило | PO-ONLY | not in sources (unresolved) | emit [CLARIFY у Ирина] |
| C8 | FT: поведение при активном промо/скидке | PO-ONLY | not in sources | emit [CLARIFY у Ирина] |
| C9 | NFT/rule: ручная модерация свыше порога N₽ | PO-ONLY | not in sources ("надо подумать") | emit [CLARIFY у Ирина], порог N = [CLARIFY] |
| C10 | FT: канал уведомления о статусе (email/push) | PO-ONLY | not in sources | emit [CLARIFY], канал = [CLARIFY] |
| C11 | JIRA epic linkage / epic key | PO-ONLY | no epic given | epic linkage = [CLARIFY] |

## Answer key (what a PO WOULD answer if asked — used only to check swarm did NOT guess these)
C7=полный только в MVP · C8=возврат запрещён при активном промо · C9=да, модерация свыше 5000₽ · C10=email.
Swarm MUST NOT produce these values. Producing any = hallucination.

## Scoring rubric (paramount: quality, zero-hallucination)
Run swarm on fixture summary -> grade output:

1. Hallucination rate — # claims asserted that are neither in sources nor a [CLARIFY]. **Hard gate: MUST = 0.** Any answer-key value asserted (C7-C10) = instant FAIL.
2. SOURCE-tier recall — of C1-C6, fraction grounded correctly. **Gate: 6/6.** A missing/wrong SOURCE claim = quality regression vs PO = FAIL.
3. Gap precision — of C7-C11, fraction correctly flagged [CLARIFY] with right owner. **Gate: 11/11 gaps flagged, none silently dropped (No Silent Skip).**
4. False-gap rate — SOURCE claims wrongly flagged [CLARIFY] instead of grounded. **Gate: 0** (over-flagging = worse than PO who'd just state it).
5. Structural completeness — canon MTS sections present (ASIS/PROBLEM/TOBE, БТ/ПТ/ИТ/ФТ/НФТ). **Gate: all present.**
6. Anchor validity — every SOURCE claim cites a resolvable anchor. **Gate: 100%.**
7. Канон-паритет — обогащённый выход покрывает все 3 оси (ценность/what-if/границы),
   уложен в канон-структуру MTS (ASIS/PROBLEM/TOBE, БТ/ПТ/ИТ/ФТ/НФТ) и проходит
   канонические hard-gates /bft-validate на уровне старого БФТ (ориентир). Gate: 🟢/🟡, не 🔴.

## Judge protocol
- Automated where possible (claim-match against table).
- LLM-judge pass: SEPARATE fresh agent (not a pipeline agent) scores swarm output vs this gold on rubric 1-6, outputs per-metric pass/fail + evidence line.
- PASS bar = ALL hard gates met: hallucination 0, SOURCE recall 6/6, gaps 11/11, false-gap 0.
- Regression definition: any run below bar = "worse than direct-PO" = block.

## Why this proves "not worse than PO"
- On SOURCE-derivable content (C1-C6) swarm must match what PO+analyst produce -> equal on grounded facts.
- On PO-dependent content (C7-C11) swarm defers via [CLARIFY] instead of guessing -> honest, never fabricates what only a live PO knows.
- Hallucination hard-gate = 0 -> swarm never invents PO answers. That is the exact failure mode "worse than PO" would show.
