import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.database.models import DailyEmission
from app.llm_agent.advisor import generate_advice
from app.ingestion.daily_job import run_daily_job

# ================================================
# CUSTOM CSS - Dark Theme with Glowing Effects
# ================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1628 0%, #1a1f3a 100%);
        border-right: 1px solid rgba(0, 255, 159, 0.2);
    }
    
    /* Metric Cards with Glow */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #00ff9f;
        text-shadow: 0 0 20px rgba(0, 255, 159, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0aec0;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        color: #00d4ff;
    }
    
    /* Headers with Gradient */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00ff9f 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Custom Card Styling */
    .custom-card {
        background: rgba(26, 31, 58, 0.6);
        border: 1px solid rgba(0, 255, 159, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 255, 159, 0.1);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        border-color: rgba(0, 255, 159, 0.5);
        box-shadow: 0 8px 32px rgba(0, 255, 159, 0.3);
        transform: translateY(-2px);
    }
    
    /* Glowing Button */
    .stButton > button {
        background: linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%);
        color: #0a0e27;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        box-shadow: 0 4px 20px rgba(0, 255, 159, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(0, 255, 159, 0.6);
        transform: translateY(-2px);
    }
    
    /* Divider Line */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(0, 255, 159, 0.5) 50%, 
            transparent 100%);
        margin: 2rem 0;
    }
    
    /* Data Table */
    .dataframe {
        background: rgba(26, 31, 58, 0.4);
        border-radius: 8px;
    }
    
    /* Caption Text */
    .caption-text {
        color: #718096;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: rgba(0, 255, 159, 0.1);
        border-left: 4px solid #00ff9f;
        color: #00ff9f;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        color: #ffc107;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #00ff9f transparent transparent transparent;
    }
    
    /* Custom Stats Card */
    .stats-card {
        background: linear-gradient(135deg, rgba(0, 255, 159, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 1px solid rgba(0, 255, 159, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .stats-label {
        color: #a0aec0;
        font-size: 1rem;
        margin-top: 8px;
    }
    
    /* Insight Box */
    .insight-box {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(138, 43, 226, 0.1) 100%);
        border-left: 4px solid #00d4ff;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);
    }
    
    /* Trend Indicator */
    .trend-up {
        color: #00ff9f;
        font-weight: 700;
    }
    
    .trend-down {
        color: #ff4757;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# ================================================
# PAGE CONFIGURATION
# ================================================
st.set_page_config(
    page_title="Carbon Copilot | AI Sustainability Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_custom_css()

# ================================================
# HEADER SECTION
# ================================================
col_header1, col_header2 = st.columns([3, 1])

with col_header1:
    st.markdown("# 🌱 Carbon Intelligence Platform")
    st.markdown('<p class="caption-text">Real-time emission tracking • AI-powered insights • Data-driven sustainability</p>', 
                unsafe_allow_html=True)

with col_header2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 10px;">
        <span style="color: #718096; font-size: 0.9rem;">Last Updated</span><br/>
        <span style="color: #00ff9f; font-weight: 600; font-size: 1.1rem;">{datetime.now().strftime('%d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

# ================================================
# DATA LOADING FUNCTIONS
# ================================================
@st.cache_data(ttl=300)
def load_data():
    db = SessionLocal()
    rows = db.query(DailyEmission).order_by(DailyEmission.date).all()
    db.close()
    
    data = [
        {
            "date": r.date,
            "fuel": r.scope1,
            "electricity": r.scope2,
            "indirect": r.scope3,
            "total": r.total
        }
        for r in rows
    ]
    return pd.DataFrame(data)

def calculate_statistics(df):
    """Calculate advanced statistics from emission data"""
    stats = {
        "total_emissions": df["total"].sum(),
        "avg_daily": df["total"].mean(),
        "max_day": df["total"].max(),
        "min_day": df["total"].min(),
        "trend_7d": ((df.tail(7)["total"].mean() - df.head(7)["total"].mean()) / df.head(7)["total"].mean() * 100) if len(df) > 14 else 0,
        "fuel_percentage": (df["fuel"].sum() / df["total"].sum() * 100),
        "electricity_percentage": (df["electricity"].sum() / df["total"].sum() * 100),
        "indirect_percentage": (df["indirect"].sum() / df["total"].sum() * 100),
    }
    return stats

# ================================================
# SIDEBAR CONTROLS
# ================================================
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("---")
    
    # Run Daily Job
    if st.button("🔄 Update Today's Emissions", use_container_width=True):
        with st.spinner("Calculating emissions..."):
            run_daily_job()
            st.success("✅ Emissions updated successfully!")
            st.cache_data.clear()
    
    st.markdown("---")
    
    # Date Range Filter (for future use)
    st.markdown("### 📅 Date Range")
    date_range = st.radio(
        "Select Period",
        ["Last 7 Days", "Last 30 Days", "All Time"],
        index=2
    )
    
    st.markdown("---")
    
    # Quick Stats in Sidebar
    st.markdown("### 📊 Quick Stats")
    
    df = load_data()
    if not df.empty:
        stats = calculate_statistics(df)
        
        st.metric(
            "Total Recorded Days",
            len(df),
            help="Number of days with emission records"
        )
        
        st.metric(
            "Average Daily CO₂",
            f"{stats['avg_daily']:.2f} kg",
            help="Mean daily emissions across all records"
        )
        
        st.metric(
            "7-Day Trend",
            f"{stats['trend_7d']:.1f}%",
            delta=f"{stats['trend_7d']:.1f}%",
            help="Change in average emissions (last 7 vs previous 7 days)"
        )

# ================================================
# MAIN DASHBOARD
# ================================================
df = load_data()

if df.empty:
    st.warning("⚠️ No emission data available. Click 'Update Today's Emissions' to generate data.")
    st.stop()

# Filter data based on date range
if date_range == "Last 7 Days":
    df = df.tail(7)
elif date_range == "Last 30 Days":
    df = df.tail(30)

# Get today's data
today = df.iloc[-1]
yesterday_total = df.iloc[-2]["total"] if len(df) > 1 else today["total"]
change_pct = ((today["total"] - yesterday_total) / yesterday_total * 100) if yesterday_total > 0 else 0

# Calculate statistics
stats = calculate_statistics(df)

# ================================================
# KEY METRICS SECTION
# ================================================
st.markdown("## 📊 Today's Carbon Footprint")
st.markdown("")

# Main metrics in 4 columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{today['total']:.1f}</p>
        <p class="stats-label">Total CO₂ (kg)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{today['fuel']:.1f}</p>
        <p class="stats-label">🚚 Fuel Emissions</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{today['electricity']:.1f}</p>
        <p class="stats-label">⚡ Electricity</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-card">
        <p class="stats-number">{today['indirect']:.1f}</p>
        <p class="stats-label">📦 Supply Chain</p>
    </div>
    """, unsafe_allow_html=True)

# Change indicator
st.markdown("")
col_change1, col_change2, col_change3 = st.columns([1, 1, 2])

with col_change1:
    trend_class = "trend-down" if change_pct < 0 else "trend-up"
    trend_icon = "📉" if change_pct < 0 else "📈"
    st.markdown(f"""
    <div class="insight-box">
        <span style="font-size: 1.2rem; font-weight: 700;">
            {trend_icon} <span class="{trend_class}">{abs(change_pct):.2f}%</span>
        </span>
        <p style="margin: 5px 0 0 0; color: #a0aec0; font-size: 0.9rem;">vs Yesterday</p>
    </div>
    """, unsafe_allow_html=True)

with col_change2:
    st.markdown(f"""
    <div class="insight-box">
        <span style="font-size: 1.2rem; font-weight: 700; color: #00d4ff;">
            {stats['avg_daily']:.1f} kg
        </span>
        <p style="margin: 5px 0 0 0; color: #a0aec0; font-size: 0.9rem;">Daily Average</p>
    </div>
    """, unsafe_allow_html=True)

with col_change3:
    dominant_source = max(
        [("Fuel", today['fuel']), ("Electricity", today['electricity']), ("Supply Chain", today['indirect'])],
        key=lambda x: x[1]
    )
    st.markdown(f"""
    <div class="insight-box">
        <span style="font-size: 1rem; font-weight: 600; color: #00ff9f;">
            💡 Dominant Source: {dominant_source[0]}
        </span>
        <p style="margin: 5px 0 0 0; color: #a0aec0; font-size: 0.9rem;">
            Contributing {(dominant_source[1]/today['total']*100):.1f}% of total emissions
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================================================
# VISUALIZATION SECTION
# ================================================
st.markdown("## 📈 Emission Analytics")
st.markdown("")

# Create two columns for charts
col_chart1, col_chart2 = st.columns(2)

# -------------------- Chart 1: Time Series --------------------
with col_chart1:
    st.markdown("### 📉 Emission Trend Over Time")
    
    fig_trend = go.Figure()
    
    # Add total emissions line
    fig_trend.add_trace(go.Scatter(
        x=df["date"],
        y=df["total"],
        mode='lines+markers',
        name='Total Emissions',
        line=dict(color='#00ff9f', width=3),
        marker=dict(size=8, color='#00ff9f', line=dict(color='#0a0e27', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 159, 0.1)'
    ))
    
    # Add moving average
    if len(df) >= 7:
        df['ma7'] = df['total'].rolling(window=7).mean()
        fig_trend.add_trace(go.Scatter(
            x=df["date"],
            y=df["ma7"],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#00d4ff', width=2, dash='dash')
        ))
    
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0aec0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="Date"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            title="CO₂ Emissions (kg)"
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

# -------------------- Chart 2: Breakdown Donut --------------------
with col_chart2:
    st.markdown("### 🎯 Today's Emission Breakdown")
    
    breakdown_df = pd.DataFrame({
        "Category": ["🚚 Fuel", "⚡ Electricity", "📦 Supply Chain"],
        "Value": [today["fuel"], today["electricity"], today["indirect"]],
        "Percentage": [
            (today["fuel"]/today["total"]*100),
            (today["electricity"]/today["total"]*100),
            (today["indirect"]/today["total"]*100)
        ]
    })
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=breakdown_df["Category"],
        values=breakdown_df["Value"],
        hole=0.5,
        marker=dict(
            colors=['#00ff9f', '#00d4ff', '#8a2be2'],
            line=dict(color='#0a0e27', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value:.2f} kg CO₂<br>%{percent}<extra></extra>'
    )])
    
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0aec0'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        annotations=[dict(
            text=f'<b>{today["total"]:.1f}</b><br>kg CO₂',
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False,
            font=dict(color='#00ff9f')
        )]
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("")

# -------------------- Chart 3: Stacked Area Chart --------------------
st.markdown("### 📊 Emission Sources Over Time")

fig_stacked = go.Figure()

fig_stacked.add_trace(go.Scatter(
    x=df["date"],
    y=df["fuel"],
    mode='lines',
    name='Fuel',
    line=dict(width=0),
    stackgroup='one',
    fillcolor='rgba(0, 255, 159, 0.6)'
))

fig_stacked.add_trace(go.Scatter(
    x=df["date"],
    y=df["electricity"],
    mode='lines',
    name='Electricity',
    line=dict(width=0),
    stackgroup='one',
    fillcolor='rgba(0, 212, 255, 0.6)'
))

fig_stacked.add_trace(go.Scatter(
    x=df["date"],
    y=df["indirect"],
    mode='lines',
    name='Supply Chain',
    line=dict(width=0),
    stackgroup='one',
    fillcolor='rgba(138, 43, 226, 0.6)'
))

fig_stacked.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#a0aec0'),
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        title="Date"
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        title="CO₂ Emissions (kg)"
    ),
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig_stacked, use_container_width=True)

st.markdown("---")

# ================================================
# AI ADVISOR SECTION
# ================================================
st.markdown("## 🤖 AI Sustainability Advisor")
st.markdown("")

col_ai1, col_ai2 = st.columns([2, 1])

with col_ai1:
    st.markdown("""
    <div class="insight-box">
        <p style="margin: 0; color: #a0aec0; font-size: 0.95rem;">
            Get personalized recommendations based on your emission patterns, 
            company context, and industry best practices powered by AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ai2:
    if st.button("✨ Generate AI Insights", use_container_width=True, type="primary"):
        with st.spinner("🧠 Analyzing emission data and generating insights..."):
            advice = generate_advice()
            
            st.markdown(f"""
            <div class="custom-card" style="margin-top: 20px;">
                <h4 style="color: #00ff9f; margin-top: 0;">💡 AI Recommendations</h4>
                <p style="color: #cbd5e0; line-height: 1.8; font-size: 1rem;">
                    {advice}
                </p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ================================================
# DATA TABLE (EXPANDABLE)
# ================================================
with st.expander("📋 View Detailed Emission Records"):
    st.markdown("### Historical Emission Data")
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%d %b %Y")
    display_df = display_df.rename(columns={
        "date": "Date",
        "fuel": "Fuel (kg CO₂)",
        "electricity": "Electricity (kg CO₂)",
        "indirect": "Supply Chain (kg CO₂)",
        "total": "Total (kg CO₂)"
    })
    
    # Round numeric columns
    numeric_cols = ["Fuel (kg CO₂)", "Electricity (kg CO₂)", "Supply Chain (kg CO₂)", "Total (kg CO₂)"]
    display_df[numeric_cols] = display_df[numeric_cols].round(2)
    
    st.dataframe(
        display_df.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"carbon_emissions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ================================================
# FOOTER
# ================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; color: #718096;">
    <p style="margin: 0;">🌱 <b>Carbon Copilot</b> - Enterprise Sustainability Intelligence Platform</p>
    <p style="margin: 5px 0 0 0; font-size: 0.85rem;">
        Powered by AI • Real-time Monitoring • Data-driven Insights
    </p>
</div>
""", unsafe_allow_html=True)
