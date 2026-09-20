# Context Maintenance Log — CCCES Dashboard (Phase I)

Purpose: running log of prompts issued, decisions made, and current state, so a
new chat session can pick up exactly where the last one left off. Append a new
entry per work session; do not delete prior entries.

---

## Session 0 — 2026-07-26
**Prompted for:** Initial planning document, YAML instrument, YAML scoring file
**Decisions made:**
- Reusing Basics4AI stack (Python/Streamlit/SQLite/GitHub/Railway) rather than a new stack
- Windows-only setup documentation for Phase I
- Mean aggregation and reverse-scoring of items 15-16 drafted as assumptions, pending PI confirmation
**Open items carried forward:**
- Adapted survey version not yet received from PI
- Reverse-scoring and aggregation method need PI sign-off
- Dashboard app not yet built

---

## Session 1 — 2026-08-13
**Prompted for:** Final PI confirmation on all remaining open decision points; vibe-code build guide and PD materials updated to reflect confirmed status.
**Decisions made:**
- Survey source: CONFIRMED — original 27-item CCCES (validated instrument). The separate 10-14 y.o. shortened version is out of scope for this build (separate/future work, not to be conflated with this dashboard).
- Reverse-scoring: CONFIRMED — items 15-16 (Attention construct) are reverse-scored, per `reverse_scoring_formula` in the scoring YAML.
- Aggregation: CONFIRMED — mean (not sum), previously confirmed.
- Hosting: CONFIRMED — local + GitHub + Railway, all three, previously confirmed.
- All four original open decision points are now resolved. No decision points remain blocking for Component A.
**Files changed:**
- `CCCES_survey_instrument.yaml` — status updated to CONFIRMED
- `CCCES_survey_scoring.yaml` — status, reverse-scored item reasons updated to CONFIRMED
- `project_status.md` — "Blocked on PI input" section cleared
- Vibe-code guide, Facilitator Handbook, Quick-Reference Card, Workshop Slides — decision-point language updated to reflect confirmed status
**Open items carried forward:**
- None blocking Component A. Dashboard build can now proceed and be scored against real data once built.

---

## Session 2 — 2026-08-13
**Prompted for:** Component A documents updated to reflect the PI's confirmation email — scope expanded from collect/score/basic-report to the full small-scale pipeline (collection → prep/scoring → statistical analysis with normality checks → interpretation → presentation). Documents brought to execution-ready state pending SoW/compensation greenlight.
**Decisions made:**
- Analysis scope CONFIRMED: descriptive statistics including per-construct/per-factor normality checks (Shapiro-Wilk) — standalone requirement for Component A, independent of Component B's separate implementation of similar descriptive analysis.
- Interpretation stage CONFIRMED as required: a plain-language narrative generated from the descriptive/normality results, verifiable against the numbers it describes.
- Instrument reconfirmed as exclusively the 27-item CCCES — no change to the YAML files themselves; the scope expansion is entirely in the app's build sequence (new Steps 4-5), not the survey/scoring definition.
**Files changed:**
- `CCCES_ClaudeDesktop_VibeCode_Guide.md` — Step 4 expanded to include normality checks; new Step 5 (Interpretation) added; former Step 5 (YAML-editability demo) renumbered to Step 6; acceptance checklist updated with two new items; scope note added.
- `CCCES_Facilitator_Handbook.docx`, `CCCES_Quick_Reference_Card.docx`, `CCCES_Workshop_Slides.pptx` — updated to describe the expanded pipeline and new build steps.
- `CCCES_survey_instrument.yaml`, `CCCES_survey_scoring.yaml` — unchanged; scope expansion is in app logic, not survey/scoring definitions.
**Open items carried forward:**
- Implementation has not yet begun — no code written. Waiting on SoW and compensation greenlight before Component A build starts from scratch, per the current agreement with the PI.
- IP/copyright specifics (which existing Basics4AI components, if any, are already flagged) remain open — see integrated implementation plan, Section 11.

---

## Session 3 — 2026-09 (live from-scratch test run on a reset test PC)
**Note on this entry:** this session's work spanned a large number of exchanges and should have been logged incrementally rather than as one retroactive entry — flagging that gap honestly rather than glossing over it.
**Prompted for:** A genuine clean-environment, timed test of the full vibe-code build guide, run by the student researcher personally on a Lenovo/Windows 11 test PC, for the purpose of reporting realistic training-session duration to the PI. The PC, GitHub account, and Railway account were all reset to a true first-time-user baseline before starting.
**Decisions made / confirmed during the run:**
- Component A's citation requirement: the instrument YAML's existing `citation` field must be displayed under the app's header — added to Step 2's build prompt and checkpoint, and to the Part 8 acceptance checklist.
- Editor choice changed from VS Code to Notepad++ throughout the guide, given repeated VS Code installer failures on the test machine; VS Code references replaced across Parts 1, 3, 4, and 5.
- All hardcoded references to the original test user's Windows username were genericized to `<YourUsername>`, with a `whoami`-based self-detection step added to Part 4.
- Established three firm standing rules for Claude Desktop's build behavior (only build what each step asks, single app.py file only, ask rather than silently assume on ambiguity) after an early run showed significant scope creep (unrequested SQLite storage, an admin/passcode tab, and a split multi-file structure all appearing at Step 2 instead of being built incrementally as later steps).
- Resolved a genuine tension between Step 2's "grouped by construct" instruction and the YAML's `randomize_items: true` flag (which reflects the original study's full-shuffle administration) — decided in favor of grouped-by-construct display for this teaching/demo build, flagged as revisitable if the app is ever used for real data collection.
**Files changed:**
- `CCCES_ClaudeDesktop_VibeCode_Guide.md` — extensively revised based on live findings, including: Claude Desktop install troubleshooting (AddPackage/MSIX failures, manual-extraction fallback, elevation quirks); Python install guidance corrected twice as python.org's download page changed; Git identity setup, PATH-staleness (fresh-terminal), and credential-flow troubleshooting; GitHub navigation fixes (Developer settings location, repo-creation default options, push-command selection); a full git-history reset procedure after manually-extracted tool folders (VSCodeManual/ClaudeManual) were accidentally committed; Railway deployment troubleshooting (GitHub App authorization, start-command requirement, log-verification-before-domain-generation, Networking/Generate Domain navigation); a live YAML-edit verification test added for the deployed Railway app; and a final explicit git-push step added to Part 9, since editing context/status files locally was never being pushed back to GitHub.
- `context_maintenance.md`, `project_status.md` — this entry itself; both were stale through the entire test run and are only being brought current now.
**Open items carried forward:**
- The live test run itself was still in progress as of this entry — Part 9's final push had not yet been confirmed done at the time of writing.
- The three-firm-rules fix to Steps 1-2 has not yet been validated on a genuinely fresh Claude Desktop conversation (it was validated via a mid-conversation correction on an already-drifted session, which is a different, weaker test) — worth a clean re-run before treating the guide as fully hardened.
- IP/copyright specifics (carried forward from Session 2) remain open.

---

## Template for future sessions

## Session N — [date]
**Prompted for:**
**Decisions made:**
**Files changed:**
**Open items carried forward:**
