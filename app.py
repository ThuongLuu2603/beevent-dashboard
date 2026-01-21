import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Beevent Dashboard 2026",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA GENERATION ====================
@st.cache_data
def generate_sample_data():
    """Generate sample data for demo"""
    np.random.seed(42)
    
    # Monthly data - FIX: Tạo 12 tháng chính xác
    months = pd.date_range('2026-01-01', periods=12, freq='MS')
    
    # Revenue by channel - FIX: Đảm bảo mỗi array có đúng 12 phần tử
    noi_bo = (np.random.randint(3000, 5000, 12) * 1000).tolist()
    gov = (np.random.randint(1000, 2000, 12) * 1000).tolist()
    corporate = (np.random.randint(1500, 2500, 12) * 1000).tolist()
    
    revenue_data = pd.DataFrame({
        'Tháng': months,
        'Nội bộ': noi_bo,
        'Gov-Hiệp hội': gov,
        'Corporate': corporate
    })
    revenue_data['Tổng DT'] = revenue_data['Nội bộ'] + revenue_data['Gov-Hiệp hội'] + revenue_data['Corporate']
    
    # Sales pipeline
    pipeline_data = pd.DataFrame({
        'Stage': ['Lead', 'Qualified', 'Proposal', 'Won'],
        'Count': [150, 95, 60, 38],
        'Value': [12000, 9500, 7200, 4800]
    })
    
    # Project data
    num_projects = 20
    projects = pd.DataFrame({
        'Dự án': [f'Event {i}' for i in range(1, num_projects + 1)],
        'Doanh thu': (np.random.randint(200, 2000, num_projects) * 1000).tolist(),
        'Lợi nhuận %': np.random.uniform(5, 25, num_projects).tolist(),
        'Khách': np.random.randint(50, 1000, num_projects).tolist(),
        'Loại': np.random.choice(['Teambuilding', 'Gala', 'Conference', 'Festival'], num_projects).tolist(),
        'CSAT': np.random.uniform(3.5, 5.0, num_projects).tolist()
    })
    
    # Sales performance
    num_sales = 12
    sales_perf = pd.DataFrame({
        'Nhân viên': [f'Sale {i}' for i in range(1, num_sales + 1)],
        'Doanh thu': (np.random.randint(300, 800, num_sales) * 1000).tolist(),
        'Số deal': np.random.randint(5, 15, num_sales).tolist(),
        'Conversion %': np.random.uniform(15, 45, num_sales).tolist(),
        'Kênh': np.random.choice(['Nội bộ', 'Gov', 'Corporate'], num_sales).tolist()
    })
    
    return revenue_data, pipeline_data, projects, sales_perf

revenue_data, pipeline_data, projects, sales_perf = generate_sample_data()

# ==================== SIDEBAR ====================
st.sidebar.title("📊 BEEVENT DASHBOARD")
st.sidebar.markdown("---")

dashboard_type = st.sidebar.radio(
    "Chọn Dashboard:",
    ["🎯 CEO/CCO - Tổng quan", "💼 Kênh bán", "📋 Dự án", "📈 So sánh kế hoạch"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Bộ lọc")

channel_filter = st.sidebar.multiselect(
    "Kênh bán:",
    ["Nội bộ", "Gov-Hiệp hội", "Corporate"],
    default=["Nội bộ", "Gov-Hiệp hội", "Corporate"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Mục tiêu 2026**\n- Doanh thu: 80 tỷ\n- Lãi gộp: 13.92 tỷ\n- LNTT: Hòa vốn")

# ==================== DASHBOARD 1: CEO/CCO ====================
if dashboard_type == "🎯 CEO/CCO - Tổng quan":
    st.markdown('<div class="main-header">🎯 DASHBOARD CEO/CCO - TỔNG QUAN CHIẾN LƯỢC</div>', unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
    target_revenue = 80_000
    revenue_achievement = (total_revenue / target_revenue) * 100
    
    with col1:
        st.metric(
            "💰 Doanh thu tích lũy",
            f"{total_revenue:,.0f}M",
            f"{revenue_achievement:.1f}% target"
        )
    
    with col2:
        gross_profit = total_revenue * 0.174
        st.metric(
            "📊 Lãi gộp",
            f"{gross_profit:,.0f}M",
            f"{(gross_profit/13920)*100:.1f}% target"
        )
    
    with col3:
        external_rate = 45
        st.metric(
            "🎯 Khách ngoài",
            f"{external_rate}%",
            f"+{external_rate-20}% vs 2025"
        )
    
    with col4:
        pipeline_coverage = 3.2
        st.metric(
            "📈 Pipeline Coverage",
            f"{pipeline_coverage:.1f}x",
            "Healthy" if pipeline_coverage >= 3 else "Warning"
        )
    
    st.markdown("---")
    
    # Row 1: Revenue by Channel
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Doanh thu theo kênh (Tích lũy)")
        
        fig_revenue = go.Figure()
        
        for channel in ['Nội bộ', 'Gov-Hiệp hội', 'Corporate']:
            if channel in channel_filter:
                fig_revenue.add_trace(go.Bar(
                    name=channel,
                    x=revenue_data['Tháng'],
                    y=revenue_data[channel] / 1_000_000,
                    text=[f"{val/1_000_000:.0f}M" for val in revenue_data[channel]],
                    textposition='inside'
                ))
        
        fig_revenue.add_trace(go.Scatter(
            name='Target tích lũy',
            x=revenue_data['Tháng'],
            y=[target_revenue/12 * (i+1) for i in range(12)],
            mode='lines+markers',
            line=dict(color='red', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig_revenue.update_layout(
            barmode='stack',
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.subheader("💧 Biên lợi nhuận (Waterfall)")
        
        cogs = total_revenue * 0.826
        operating_cost = gross_profit * 0.95
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Cash Flow",
            orientation="v",
            measure=["relative", "relative", "total", "relative", "total"],
            x=["Doanh thu", "COGS", "Lãi gộp", "Chi phí VH", "LNTT"],
            y=[total_revenue, -cogs, 0, -operating_cost, 0],
            text=[f"{total_revenue:,.0f}M", f"{-cogs:,.0f}M", f"{gross_profit:,.0f}M", 
                  f"{-operating_cost:,.0f}M", f"{gross_profit-operating_cost:,.0f}M"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#ff6b6b"}},
            increasing={"marker": {"color": "#51cf66"}},
            totals={"marker": {"color": "#1f77b4"}}
        ))
        
        fig_waterfall.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Pipeline Funnel + Customer Mix
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Pipeline Coverage")
        
        fig_funnel = go.Figure(go.Funnel(
            y=pipeline_data['Stage'],
            x=pipeline_data['Count'],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]),
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}}
        ))
        
        fig_funnel.update_layout(height=400)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        conversion_rate = (pipeline_data.iloc[-1]['Count'] / pipeline_data.iloc[0]['Count']) * 100
        st.info(f"📊 **Conversion Rate:** {conversion_rate:.1f}% | **Win Value:** {pipeline_data.iloc[-1]['Value']}M")
    
    with col2:
        st.subheader("🥧 Cơ cấu khách hàng")
        
        customer_mix = pd.DataFrame({
            'Loại': ['Nội bộ', 'Bên ngoài'],
            'Tỷ lệ': [55, 45]
        })
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=customer_mix['Loại'],
            values=customer_mix['Tỷ lệ'],
            hole=0.5,
            marker=dict(colors=['#1f77b4', '#ff7f0e']),
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig_donut.update_layout(
            height=400,
            annotations=[dict(text='Customer<br>Mix', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        st.success("✅ Đạt mục tiêu cơ cấu khách hàng 55/45")

# ==================== DASHBOARD 2: KÊNH BÁN ====================
elif dashboard_type == "💼 Kênh bán":
    st.markdown('<div class="main-header">💼 DASHBOARD KÊNH BÁN - HIỆU SUẤT KINH DOANH</div>', unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Tổng Lead", "150", "+12 tuần này")
    
    with col2:
        st.metric("✅ Win Rate", "25.3%", "+3.2%")
    
    with col3:
        avg_deal = sales_perf['Doanh thu'].mean() / sales_perf['Số deal'].mean()
        st.metric("💵 AOV", f"{avg_deal/1000:.0f}M", "+15%")
    
    with col4:
        st.metric("⏱️ Avg. Close Time", "18 ngày", "-3 ngày")
    
    st.markdown("---")
    
    # Row 1: Sankey
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🔄 Lead Flow (Sankey)")
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Lead", "Qualified", "Proposal", "Won", "Lost"],
                color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#7f7f7f"]
            ),
            link=dict(
                source=[0, 0, 1, 1, 2, 2],
                target=[1, 4, 2, 4, 3, 4],
                value=[95, 55, 60, 35, 38, 22],
                color=["rgba(31,119,180,0.3)", "rgba(127,127,127,0.3)", 
                       "rgba(255,127,14,0.3)", "rgba(127,127,127,0.3)",
                       "rgba(44,160,44,0.3)", "rgba(127,127,127,0.3)"]
            )
        )])
        
        fig_sankey.update_layout(height=400, font_size=12)
        st.plotly_chart(fig_sankey, use_container_width=True)
    
    with col2:
        st.subheader("📊 Phân bố giá trị Deal")
        
        deal_values = np.random.lognormal(13, 1, 100) / 1000
        
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=deal_values,
            name="All Deals",
            boxmean='sd',
            marker_color='#1f77b4'
        ))
        
        fig_box.update_layout(
            height=400,
            yaxis_title="Giá trị (M VNĐ)",
            showlegend=False
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
        st.info(f"📊 **Median:** {np.median(deal_values):.1f}M | **Mean:** {np.mean(deal_values):.1f}M")
    
    st.markdown("---")
    
    # Sales Performance
    st.subheader("🏆 Bảng xếp hạng Sales Performance")
    
    sales_perf_sorted = sales_perf.sort_values('Doanh thu', ascending=False).reset_index(drop=True)
    sales_perf_sorted['Rank'] = range(1, len(sales_perf_sorted) + 1)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        top_5 = sales_perf_sorted.head(5)[['Rank', 'Nhân viên', 'Doanh thu', 'Số deal', 'Conversion %']].copy()
        top_5['Doanh thu'] = top_5['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
        top_5['Conversion %'] = top_5['Conversion %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(top_5, hide_index=True, use_container_width=True, height=250)
    
    with col2:
        fig_scatter = px.scatter(
            sales_perf,
            x='Số deal',
            y='Doanh thu',
            size='Conversion %',
            color='Kênh',
            hover_data=['Nhân viên'],
            title="Hiệu suất theo Số deal vs Doanh thu"
        )
        
        fig_scatter.update_layout(height=300)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==================== DASHBOARD 3: DỰ ÁN ====================
elif dashboard_type == "📋 Dự án":
    st.markdown('<div class="main-header">📋 DASHBOARD DỰ ÁN - QUẢN TRỊ VẬN HÀNH</div>', unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Dự án đang chạy", "12", "+3 vs tháng trước")
    
    with col2:
        avg_profit = projects['Lợi nhuận %'].mean()
        st.metric("💰 Biên LN TB", f"{avg_profit:.1f}%", "+2.3%")
    
    with col3:
        avg_csat = projects['CSAT'].mean()
        st.metric("⭐ CSAT TB", f"{avg_csat:.2f}/5", "+0.15")
    
    with col4:
        cost_variance = 8.5
        st.metric("📊 Cost Variance", f"{cost_variance:.1f}%", "Trong kiểm soát")
    
    st.markdown("---")
    
    # Project Profitability Scatter
    st.subheader("💎 Ma trận Doanh thu - Lợi nhuận các Event")
    
    fig_scatter = px.scatter(
        projects,
        x='Doanh thu',
        y='Lợi nhuận %',
        size='Khách',
        color='Loại',
        hover_data=['Dự án', 'CSAT'],
        title="Bubble size = Số lượng khách"
    )
    
    fig_scatter.add_hline(y=projects['Lợi nhuận %'].median(), line_dash="dash", line_color="gray")
    fig_scatter.add_vline(x=projects['Doanh thu'].median(), line_dash="dash", line_color="gray")
    
    fig_scatter.update_layout(height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.info("💡 **Insight:** Tập trung nhân rộng các event ở góc phải trên (DT cao + LN cao)")
    
    st.markdown("---")
    
    # CSAT Distribution
    st.subheader("⭐ Phân bố CSAT & Chi tiết dự án")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        csat_bins = pd.cut(projects['CSAT'], bins=[0, 3, 3.5, 4, 4.5, 5], labels=['1-3', '3-3.5', '3.5-4', '4-4.5', '4.5-5'])
        csat_dist = csat_bins.value_counts().sort_index()
        
        fig_csat = go.Figure(data=[go.Bar(
            x=csat_dist.index.astype(str),
            y=csat_dist.values,
            marker_color=['#ff6b6b', '#ffa94d', '#ffd43b', '#51cf66', '#37b24d']
        )])
        
        fig_csat.update_layout(height=300, xaxis_title="Điểm CSAT", yaxis_title="Số lượng event")
        st.plotly_chart(fig_csat, use_container_width=True)
    
    with col2:
        low_csat = projects[projects['CSAT'] < 4.0][['Dự án', 'Loại', 'Doanh thu', 'CSAT']].sort_values('CSAT').copy()
        
        if len(low_csat) > 0:
            low_csat['Doanh thu'] = low_csat['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
            st.dataframe(low_csat, hide_index=True, use_container_width=True, height=300)
        else:
            st.success("🎉 Không có dự án nào có CSAT < 4.0!")

# ==================== DASHBOARD 4: SO SÁNH ====================
else:
    st.markdown('<div class="main-header">📈 SO SÁNH KẾ HOẠCH VS THỰC TẾ</div>', unsafe_allow_html=True)
    
    total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
    gross_profit = total_revenue * 0.174
    avg_csat = projects['CSAT'].mean()
    
    comparison = pd.DataFrame({
        'Chỉ tiêu': ['Doanh thu', 'Lãi gộp', 'LNTT', 'Số dự án', 'CSAT TB'],
        'KH 2026': [80000, 13920, 82, 120, 4.2],
        'TH hiện tại': [total_revenue, gross_profit, 45, 85, avg_csat],
        'Đơn vị': ['M', 'M', 'M', 'dự án', 'điểm']
    })
    
    comparison['% Hoàn thành'] = (comparison['TH hiện tại'] / comparison['KH 2026'] * 100).round(1)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Bảng so sánh chi tiết")
        st.dataframe(comparison, hide_index=True, use_container_width=True, height=250)
    
    with col2:
        st.subheader("🎯 Tỷ lệ hoàn thành")
        
        revenue_achievement = (total_revenue / 80000) * 100
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=revenue_achievement,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Doanh thu", 'font': {'size': 24}},
            delta={'reference': 100, 'suffix': "%"},
            gauge={
                'axis': {'range': [None, 120]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': '#ff6b6b'},
                    {'range': [50, 80], 'color': '#ffd43b'},
                    {'range': [80, 100], 'color': '#51cf66'},
                    {'range': [100, 120], 'color': '#37b24d'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown("---")
    
    # Monthly trend
    st.subheader("📈 Xu hướng theo tháng: KH vs TH")
    
    target_revenue = 80000
    monthly_comparison = pd.DataFrame({
        'Tháng': revenue_data['Tháng'],
        'KH tích lũy': [target_revenue/12 * (i+1) for i in range(12)],
        'TH tích lũy': (revenue_data['Tổng DT'].cumsum() / 1_000_000).tolist()
    })
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=monthly_comparison['Tháng'],
        y=monthly_comparison['KH tích lũy'],
        mode='lines+markers',
        name='Kế hoạch',
        line=dict(color='red', width=3, dash='dash'),
        marker=dict(size=8)
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=monthly_comparison['Tháng'],
        y=monthly_comparison['TH tích lũy'],
        mode='lines+markers',
        name='Thực hiện',
        line=dict(color='blue', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    fig_trend.update_layout(height=400, hovermode='x unified', yaxis_title="Doanh thu tích lũy (M VNĐ)")
    st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Beevent Dashboard 2026</strong> | Powered by Streamlit & Plotly</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
