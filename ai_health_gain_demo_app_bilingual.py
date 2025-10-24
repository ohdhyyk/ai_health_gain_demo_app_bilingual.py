import streamlit as st
import io
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI Health Gain — Demo (EN/NO)", page_icon="🌿", layout="centered")

# ------------------------
# Minimal CSS for a modern look & top-left language switcher
# ------------------------
st.markdown(
    """
    <style>
      html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      }
      :root { --uio-red: #9b1c1c; }
      .uio-accent { color: var(--uio-red) !important; }
      .card {
        border: 1px solid rgba(0,0,0,0.07);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 10px rgba(0,0,0,0.06);
        background: #fff;
      }
      .lang-switch { position: sticky; top: 0; left: 0; z-index: 100; padding-top: 6px; margin-bottom: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# Language state & strings
# ------------------------
if "lang" not in st.session_state:
  st.session_state["lang"] = "EN"  # default EN

with st.container():
  st.markdown('<div class="lang-switch">', unsafe_allow_html=True)
  cols = st.columns([0.22, 0.78])
  with cols[0]:
    choice = st.radio("", options=["NO", "EN"], horizontal=True,
                      index=0 if st.session_state["lang"] == "NO" else 1,
                      label_visibility="collapsed")
    st.session_state["lang"] = choice
  with cols[1]:
    st.write("")
  st.markdown('</div>', unsafe_allow_html=True)

LANG = st.session_state["lang"]

S = {
  "EN": {
    "title": "🌿 AI Health Gain — Demo",
    "subtitle": "See how small changes can lead to **visible health gains**. *Educational concept — not medical advice.*",
    "age": "Age (years)",
    "sex": "Gender",
    "male": "Male",
    "female": "Female",
    "years_drink": "Years of drinking",
    "days_now": "Current drinking days per week",
    "drinks_per": "Approx. drinks per occasion",
    "days_goal": "Goal: reduce drinking days to",
    "calc": "Calculate health gain",
    "your_gain": "Your estimated gain",
    "lifespan_bar": "**Health lifespan bar**",
    "tips": "### 💬 Gentle tips",
    "tip_good_start": "- Great start — moving from **{x}** to **{y}** days. Keep this pace 🌱",
    "tip_reduce_one": "- If helpful, reduce by 1 day first and build your rhythm.",
    "tip_support": "- Eating before drinking and ~3 workouts/week can further support heart health.",
    "tip_try_reduce": "- Try reducing by 1 day per week first and build a sustainable rhythm.",
    "see_details": "See model details (demo, explainable)",
    "save_result": "### ⬇️ Save your result",
    "download_txt": "Download summary (.txt)",
    "download_csv": "Download data (.csv)",
    "disclaimer": "Disclaimer: Educational demo only — not medical advice. Parameters are placeholders and will be calibrated with peer‑reviewed evidence and local data.",
    "headline": "If you reduce your drinking days from {now} to {goal} per week, you could gain about +{months} months of healthy life."
  },
  "NO": {
    "title": "🌿 AI Health Gain — Demo",
    "subtitle": "Se hvordan små endringer kan gi **synlige helseeffekter**. *Kun for læring — ikke medisinske råd.*",
    "age": "Alder (år)",
    "sex": "Kjønn",
    "male": "Mann",
    "female": "Kvinne",
    "years_drink": "Antall år med alkoholbruk",
    "days_now": "Nåværende drikkedager per uke",
    "drinks_per": "Omtrentlig antall enheter per anledning",
    "days_goal": "Mål: reduser drikkedager til",
    "calc": "Beregn helseeffekt",
    "your_gain": "Din estimerte gevinst",
    "lifespan_bar": "**Helse‑leveår (indikator)**",
    "tips": "### 💬 Enkle råd",
    "tip_good_start": "- God start — fra **{x}** til **{y}** dager. Fortsett i denne rytmen 🌱",
    "tip_reduce_one": "- Om det hjelper, reduser først med 1 dag og bygg vanen gradvis.",
    "tip_support": "- Å spise før man drikker og ~3 økter/uke kan støtte hjertehelsen.",
    "tip_try_reduce": "- Prøv å redusere med 1 dag per uke først og bygg et bærekraftig mønster.",
    "see_details": "Se modell‑detaljer (demo, forklarbar)",
    "save_result": "### ⬇️ Lagre resultatet",
    "download_txt": "Last ned sammendrag (.txt)",
    "download_csv": "Last ned data (.csv)",
    "disclaimer": "Forbehold: Kun et lærings‑demo — ikke medisinske råd. Parametere er plassholdere og skal kalibreres mot fagfellevurdert kunnskap og lokale data.",
    "headline": "Hvis du reduserer drikkedager fra {now} til {goal} per uke, kan du få omtrent +{months} måneder i god helse."
  }
}

# ------------------------
# Core model (same as your demo)
# ------------------------
def health_gain_demo(age, sex, drinking_days, drinks_per_occ, years_drinking, target_days):
  drinks_per_week_now = drinking_days * drinks_per_occ
  drinks_per_week_after = target_days * drinks_per_occ

  binge_now = 1 if drinks_per_occ >= 5 else 0
  binge_after = binge_now  # only changing days in this demo

  # Placeholder parameters (to be calibrated with literature later)
  a, b, c = 0.02, 0.15, 0.10
  sex_adj = 0.95 if str(sex).lower() in ["female", "f", "woman", "kvinne"] else 1.0
  age_adj = max(0.6, 1.2 - (age - 20) * 0.01)  # from ~1.2 at 20y to ~0.6 at 80y
  adjust = sex_adj * age_adj

  rr_now = 1 + a * drinks_per_week_now + b * binge_now + c * (years_drinking / 20.0)
    # ^^^^^^ fixing indentation
  rr_after = 1 + a * drinks_per_week_after + b * binge_after + c * (years_drinking / 20.0)

  rr_now = max(rr_now, 0.8)
  rr_after = max(rr_after, 0.8)

  k = 8.0
  gain_years = k * (rr_now - rr_after) / rr_now * adjust

  gain_years = max(0.0, min(gain_years, 3.0))  # cap at +3 years for demo visuals
  gain_months = round(gain_years * 12)

  headline = S[LANG]["headline"].format(now=drinking_days, goal=target_days, months=gain_months)
  detail = {
      "age": age, "sex": sex,
      "now_drinks_per_week": drinks_per_week_now,
      "after_drinks_per_week": drinks_per_week_after,
      "rr_now": round(rr_now, 3),
      "rr_after": round(rr_after, 3),
      "gain_years": round(gain_years, 2),
      "gain_months": gain_months
  }
  return headline, detail

# ------------------------
# UI
# ------------------------
st.markdown(f"# <span class='uio-accent'>{S[LANG]['title']}</span>", unsafe_allow_html=True)
st.markdown(S[LANG]["subtitle"])

with st.container():
  st.markdown("<div class='card'>", unsafe_allow_html=True)
  with st.form("inputs"):
    col1, col2 = st.columns(2)
    with col1:
      age = st.number_input(S[LANG]["age"], min_value=15, max_value=90, value=28, step=1)
      sex = st.selectbox(S[LANG]["sex"], [S[LANG]["male"], S[LANG]["female"]])
      years_drinking = st.number_input(S[LANG]["years_drink"], min_value=0, max_value=60, value=5, step=1)
    with col2:
      drinking_days = st.slider(S[LANG]["days_now"], 0, 7, 4)
      drinks_per_occ = st.slider(S[LANG]["drinks_per"], 0, 10, 2)
      target_days = st.slider(S[LANG]["days_goal"], 0, 7, 2)

    submitted = st.form_submit_button(S[LANG]["calc"])
  st.markdown("</div>", unsafe_allow_html=True)

if submitted:
  st.subheader(S[LANG]["your_gain"])
  headline, detail = health_gain_demo(
      age=age, sex=sex, drinking_days=drinking_days,
      drinks_per_occ=drinks_per_occ, years_drinking=years_drinking,
      target_days=target_days
  )
  st.success(headline)

  st.markdown(S[LANG]["lifespan_bar"])
  cap_months = 36
  progress = min(detail["gain_months"], cap_months) / cap_months
  st.progress(progress)

  st.markdown(S[LANG]["tips"])
  if target_days < drinking_days:
    st.write(S[LANG]["tip_good_start"].format(x=drinking_days, y=target_days))
    if drinking_days - target_days >= 2:
      st.write(S[LANG]["tip_reduce_one"])
    st.write(S[LANG]["tip_support"])
  else:
    st.write(S[LANG]["tip_try_reduce"])

  with st.expander(S[LANG]["see_details"]):
    st.json(detail)

  # ---- Downloads ----
  st.markdown("---")
  st.markdown(S[LANG]["save_result"])
  txt = f"""AI Health Gain – Demo Result
Time: {datetime.utcnow().isoformat()}Z

{headline}

Inputs:
- Age: {detail['age']}
- Sex: {detail['sex']}
- Drinking days (now→goal): {drinking_days} → {target_days}
- Drinks per occasion: {drinks_per_occ}
- Years drinking: {years_drinking}

Model (demo):
- RR now / after: {detail['rr_now']} / {detail['rr_after']}
- Healthy life gain: {detail['gain_months']} months
"""
  st.download_button(S[LANG]["download_txt"], txt, file_name="ai_health_gain_result.txt")

  df = pd.DataFrame([detail])
  csv_buf = io.StringIO()
  df.to_csv(csv_buf, index=False)
  st.download_button(S[LANG]["download_csv"], csv_buf.getvalue(), file_name="ai_health_gain_result.csv")

st.markdown("---")
st.caption(S[LANG]["disclaimer"])
