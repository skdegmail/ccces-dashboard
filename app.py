"""
app.py -- CCCES Dashboard (Streamlit)

STEP 3 OF THE BUILD: adds a second tab, "Aggregate Results," that reads
every saved response back out of responses.db (not from in-memory state)
and shows:
    - total number of responses saved
    - per-construct and per-factor mean score across all saved responses
    - overall mean total score across all saved responses
    - a Shapiro-Wilk normality test (scipy.stats.shapiro) for each
      construct's and each factor's saved scores, showing the actual
      statistic and p-value, a plain-language flag, and a bar chart of
      the individual scores that went into that test
    - a plain "not enough responses yet" note (instead of an error) when
      fewer than 3 responses exist, since Shapiro-Wilk requires at least 3

Display choice (unchanged from previous steps): items are grouped and
labeled by construct (with construct headers shown), even though the
instrument YAML sets randomize_items: true at the survey level. For this
teaching/demo build, grouped display is more useful than exact
original-study item randomization; that can be revisited if this becomes
the real data-collection instrument.

Scoring rules (from CCCES_survey_scoring.yaml), applied per submission:
    - Items 15 and 16 are reverse-scored first, using
      (scale_max + scale_min) - raw_score.
    - Construct scores = MEAN of that construct's (reverse-adjusted) items.
    - Factor scores = MEAN of the construct scores within that factor.
    - Total score = MEAN across all 27 (reverse-adjusted) items.

Run locally with:
    streamlit run app.py

Files this app expects to find alongside it:
    CCCES_survey_instrument.yaml
    CCCES_survey_scoring.yaml
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import yaml
from scipy.stats import shapiro

APP_DIR = Path(__file__).parent
INSTRUMENT_PATH = APP_DIR / "CCCES_survey_instrument.yaml"
SCORING_PATH = APP_DIR / "CCCES_survey_scoring.yaml"
DB_PATH = APP_DIR / "responses.db"

SHAPIRO_MIN_N = 3


# ---------------------------------------------------------------------------
# Load the instrument and scoring rules (cached so we don't re-parse YAML or
# re-touch the database on every rerun)
# ---------------------------------------------------------------------------

@st.cache_resource
def load_instrument():
    with open(INSTRUMENT_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["survey"]


@st.cache_resource
def load_scoring():
    with open(SCORING_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["scoring"]


@st.cache_resource
def ensure_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submitted_at_utc TEXT NOT NULL,
                raw_responses_json TEXT NOT NULL,
                construct_scores_json TEXT NOT NULL,
                factor_scores_json TEXT NOT NULL,
                total_score REAL NOT NULL
            )
            """
        )
        conn.commit()
    return True


instrument = load_instrument()
scoring = load_scoring()
ensure_db()

st.set_page_config(page_title=instrument["title"], layout="centered")


# ---------------------------------------------------------------------------
# Build a lookup of construct -> ordered list of its items, preserving the
# construct order given in the YAML's top-level "constructs" list, and the
# item order given in the YAML's "items" list within each construct.
# ---------------------------------------------------------------------------

def group_items_by_construct(survey_dict):
    construct_order = [c["id"] for c in survey_dict["constructs"]]
    construct_labels = {c["id"]: c["label"] for c in survey_dict["constructs"]}

    grouped = {cid: [] for cid in construct_order}
    for item in survey_dict["items"]:
        grouped[item["construct"]].append(item)

    return construct_order, construct_labels, grouped


construct_order, construct_labels, items_by_construct = group_items_by_construct(instrument)

anchors = instrument["response_scale"]["anchors"]  # {1: "Never", ..., 5: "Always"}
scale_points = sorted(anchors.keys())
option_labels = [anchors[p] for p in scale_points]

total_item_count = sum(len(items) for items in items_by_construct.values())


# ---------------------------------------------------------------------------
# Scoring, per CCCES_survey_scoring.yaml
# ---------------------------------------------------------------------------

def score_responses(raw_responses, scoring_dict):
    """
    raw_responses: {item_id (int): raw_score (int, 1-5)}
    Returns (scored_items, construct_scores, factor_scores, total_score).
    """
    scale_min, scale_max = scoring_dict["scale_range"]
    reverse_ids = {entry["id"] for entry in scoring_dict["reverse_scored_items"]}

    scored_items = {}
    for item_id, raw in raw_responses.items():
        if item_id in reverse_ids:
            scored_items[item_id] = (scale_max + scale_min) - raw
        else:
            scored_items[item_id] = raw

    construct_scores = {}
    for construct in scoring_dict["constructs"]:
        values = [scored_items[i] for i in construct["items"]]
        construct_scores[construct["id"]] = sum(values) / len(values)

    factor_scores = {}
    for factor in scoring_dict["factors"]:
        values = [construct_scores[cid] for cid in factor["constructs"]]
        factor_scores[factor["id"]] = sum(values) / len(values)

    total_score = sum(scored_items.values()) / len(scored_items)

    return scored_items, construct_scores, factor_scores, total_score


def save_response(raw_responses, construct_scores, factor_scores, total_score):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO responses (
                submitted_at_utc, raw_responses_json,
                construct_scores_json, factor_scores_json, total_score
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                json.dumps({str(k): v for k, v in raw_responses.items()}),
                json.dumps({str(k): v for k, v in construct_scores.items()}),
                json.dumps({str(k): v for k, v in factor_scores.items()}),
                total_score,
            ),
        )
        conn.commit()


def fetch_all_saved_scores():
    """
    Reads every saved response from responses.db and returns:
        (
            total_response_count,
            construct_score_lists,   # {construct_id: [score, score, ...]}
            factor_score_lists,      # {factor_id: [score, score, ...]}
            total_score_list,        # [score, score, ...]
        )
    Pulled fresh from the database every call -- not from in-memory state.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM responses ORDER BY id").fetchall()

    construct_score_lists = {c["id"]: [] for c in scoring["constructs"]}
    factor_score_lists = {f["id"]: [] for f in scoring["factors"]}
    total_score_list = []

    for row in rows:
        construct_scores = json.loads(row["construct_scores_json"])
        factor_scores = json.loads(row["factor_scores_json"])

        for construct in scoring["constructs"]:
            construct_score_lists[construct["id"]].append(construct_scores[construct["id"]])
        for factor in scoring["factors"]:
            factor_score_lists[factor["id"]].append(factor_scores[str(factor["id"])])
        total_score_list.append(row["total_score"])

    return len(rows), construct_score_lists, factor_score_lists, total_score_list


def compute_shapiro(values):
    """
    Returns a dict describing the normality check for one score list:
        {"sufficient": bool, "statistic": float or None,
         "p_value": float or None, "is_normal": bool or None}
    "is_normal" is None whenever there isn't enough data to run the test.
    """
    if len(values) < SHAPIRO_MIN_N:
        return {"sufficient": False, "statistic": None, "p_value": None, "is_normal": None}
    statistic, p_value = shapiro(values)
    return {
        "sufficient": True,
        "statistic": statistic,
        "p_value": p_value,
        "is_normal": p_value > 0.05,
    }


def render_normality_check(label, values):
    """
    Renders the statistic, p-value, plain-language flag, and bar chart of
    individual scores for one construct or factor's saved score list.
    Returns the compute_shapiro() result so callers can reuse it.
    """
    result = compute_shapiro(values)

    st.markdown(f"**{label}**")
    st.write(f"Mean: {sum(values) / len(values):.2f}  (n = {len(values)})")

    if not result["sufficient"]:
        st.info(
            f"Not enough responses yet for a Shapiro-Wilk test "
            f"(needs at least {SHAPIRO_MIN_N}; {len(values)} saved so far)."
        )
    else:
        st.write(f"Shapiro-Wilk statistic: {result['statistic']:.4f}")
        st.write(f"p-value: {result['p_value']:.4f}")
        if result["is_normal"]:
            st.write("appears normally distributed")
        else:
            st.write("does not appear normally distributed (may need a different approach if compared later)")

    st.bar_chart(values)
    st.divider()

    return result


def generate_interpretation(construct_score_lists, factor_score_lists, total_score_list):
    """
    Builds a short, plain-language interpretation paragraph (3-4 sentences)
    from the current aggregate data: highest- and lowest-scoring constructs,
    the overall total mean, and any construct/factor flagged as not normally
    distributed.
    """
    construct_means = {
        cid: sum(values) / len(values) for cid, values in construct_score_lists.items()
    }
    highest_cid = max(construct_means, key=construct_means.get)
    lowest_cid = min(construct_means, key=construct_means.get)
    total_mean = sum(total_score_list) / len(total_score_list)

    non_normal_labels = []
    for construct in scoring["constructs"]:
        cid = construct["id"]
        result = compute_shapiro(construct_score_lists[cid])
        if result["is_normal"] is False:
            non_normal_labels.append(construct_labels[cid])
    for factor in scoring["factors"]:
        result = compute_shapiro(factor_score_lists[factor["id"]])
        if result["is_normal"] is False:
            non_normal_labels.append(factor["label"])

    sentence_1 = (
        f"Across all saved responses, the overall total mean score was {total_mean:.2f}."
    )
    sentence_2 = (
        f"{construct_labels[highest_cid]} had the highest average score "
        f"({construct_means[highest_cid]:.2f}), while {construct_labels[lowest_cid]} had the "
        f"lowest ({construct_means[lowest_cid]:.2f})."
    )
    if non_normal_labels:
        sentence_3 = (
            f"{', '.join(non_normal_labels)} did not appear normally distributed, which "
            f"matters because it may call for a different statistical approach if someone "
            f"later wants to run a comparison test on those scores."
        )
    else:
        sentence_3 = (
            "All constructs and factors with enough data so far appeared normally "
            "distributed, so standard comparison tests should be usable if needed later."
        )

    return " ".join([sentence_1, sentence_2, sentence_3])


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

survey_tab, results_tab = st.tabs(["Take the Survey", "Aggregate Results"])

with survey_tab:
    st.title(instrument["title"])
    st.caption(instrument["citation"].strip())
    st.write(instrument["global_instructions"].strip())
    st.divider()

    with st.form("ccces_form", clear_on_submit=False):
        question_number = 0
        for construct_id in construct_order:
            items = items_by_construct[construct_id]
            if not items:
                continue

            st.subheader(construct_labels[construct_id])
            for item in items:
                question_number += 1
                st.radio(
                    f"{question_number}. {item['text']}",
                    options=option_labels,
                    index=None,
                    key=f"item_{item['id']}",
                    horizontal=True,
                )
            st.divider()

        submitted = st.form_submit_button("Submit survey", use_container_width=True)

    # -----------------------------------------------------------------
    # Validate completeness, then score and save
    # -----------------------------------------------------------------

    if submitted:
        unanswered_numbers = []
        question_number = 0
        for construct_id in construct_order:
            for item in items_by_construct[construct_id]:
                question_number += 1
                if st.session_state.get(f"item_{item['id']}") is None:
                    unanswered_numbers.append(question_number)

        if unanswered_numbers:
            st.error(
                f"Please answer all {total_item_count} items before submitting. "
                f"{len(unanswered_numbers)} item(s) still need a response "
                f"(question number(s): {', '.join(str(n) for n in unanswered_numbers)})."
            )
        else:
            label_to_score = {anchors[p]: p for p in scale_points}
            raw_responses = {}
            for construct_id in construct_order:
                for item in items_by_construct[construct_id]:
                    raw_responses[item["id"]] = label_to_score[st.session_state[f"item_{item['id']}"]]

            scored_items, construct_scores, factor_scores, total_score = score_responses(
                raw_responses, scoring
            )
            save_response(raw_responses, construct_scores, factor_scores, total_score)

            st.success(f"All {total_item_count} items answered. Your response has been saved.")

            st.subheader("Your score breakdown")

            st.markdown("**Construct means**")
            for construct in scoring["constructs"]:
                cid = construct["id"]
                st.write(f"- {construct_labels[cid]}: {construct_scores[cid]:.2f}")

            st.markdown("**Factor means**")
            for factor in scoring["factors"]:
                st.write(f"- {factor['label']}: {factor_scores[factor['id']]:.2f}")

            st.markdown("**Overall total mean**")
            st.write(f"{total_score:.2f}")

with results_tab:
    st.title("Aggregate Results")

    response_count, construct_score_lists, factor_score_lists, total_score_list = (
        fetch_all_saved_scores()
    )

    st.metric("Total responses saved", response_count)

    if response_count == 0:
        st.info("No responses have been saved yet.")
    else:
        st.divider()

        st.header("Construct scores")
        for construct in scoring["constructs"]:
            cid = construct["id"]
            render_normality_check(construct_labels[cid], construct_score_lists[cid])

        st.header("Factor scores")
        for factor in scoring["factors"]:
            render_normality_check(factor["label"], factor_score_lists[factor["id"]])

        st.header("Overall total score")
        st.write(f"Mean across all saved responses: {sum(total_score_list) / len(total_score_list):.2f}")

        st.header("Plain-language summary")
        st.write(
            generate_interpretation(construct_score_lists, factor_score_lists, total_score_list)
        )
