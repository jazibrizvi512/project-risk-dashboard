import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Project Risk Dashboard", layout="wide")

st.title("🏗️ Project Risk & Performance Dashboard")
st.markdown("A professional dashboard to monitor budget, schedule, and risks.")

# --- Sidebar Inputs ---
st.sidebar.header("Project Inputs")
name = st.sidebar.text_input("Project Name", "132kV Grid Station Expansion")
budget = st.sidebar.number_input("Total Budget", min_value=0.0, value=1_000_000.0, step=10_000.0)
spent = st.sidebar.number_input("Spent Amount", min_value=0.0, value=400_000.0, step=10_000.0)
planned_months = st.sidebar.number_input("Planned Duration (months)", min_value=1, value=12)
actual_months = st.sidebar.number_input("Actual Duration (months so far)", min_value=0, value=8)
progress = st.sidebar.slider("Progress (%)", 0, 100, 50)

# Risk register input
st.sidebar.markdown("### Risks (comma separated)")
risks_text = st.sidebar.text_area("Enter risks", "Delay in material delivery, Permit issue")

# --- Calculations ---
budget_variance = budget - spent
planned_progress = (actual_months / planned_months) * 100 if planned_months > 0 else 0
schedule_performance = round(progress / planned_progress, 2) if planned_progress > 0 else 1.0
cost_performance = round(progress / ((spent / budget) * 100), 2) if spent > 0 else 1.0

# Risk classification
risk_list = [r.strip() for r in risks_text.split(",") if r.strip()]
risk_df = pd.DataFrame(risk_list, columns=["Risk"])
risk_df["Severity"] = risk_df["Risk"].apply(
    lambda x: "High" if any(k in x.lower() for k in ["delay", "shortage", "permit", "issue"])
    else "Low"
)

# --- KPIs ---
st.subheader(f"📊 Project Report: {name}")
col1, col2, col3 = st.columns(3)
col1.metric("Budget Variance", f"${budget_variance:,.0f}")
col2.metric("SPI (Schedule Perf.)", schedule_performance)
col3.metric("CPI (Cost Perf.)", cost_performance)

# --- Charts ---
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Budget Overview")
    fig, ax = plt.subplots()
    ax.bar(["Budget", "Spent"], [budget, spent], color=["green", "red"])
    ax.set_ylabel("Amount ($)")
    st.pyplot(fig)

with c2:
    st.markdown("#### Schedule Progress")
    fig2, ax2 = plt.subplots()
    ax2.bar(["Planned Progress", "Actual Progress"], [planned_progress, progress], color=["blue", "orange"])
    ax2.set_ylabel("Progress (%)")
    st.pyplot(fig2)

# --- Risk Register ---
st.markdown("#### Risk Register")
st.dataframe(risk_df, use_container_width=True)

# --- Export PDF Report ---
def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(f"Project Report: {name}", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Budget Variance: ${budget_variance:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Schedule Performance Index: {schedule_performance}", styles["Normal"]))
    elements.append(Paragraph(f"Cost Performance Index: {cost_performance}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Risks:", styles["Heading2"]))
    for _, row in risk_df.iterrows():
        elements.append(Paragraph(f"- {row['Risk']} ({row['Severity']})", styles["Normal"]))
    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("📥 Download Project Report as PDF"):
    pdf = generate_pdf()
    st.download_button("Download Report", data=pdf, file_name="project_report.pdf", mime="application/pdf")