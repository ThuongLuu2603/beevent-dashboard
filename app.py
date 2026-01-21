import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GOOGLE SHEETS CONNECTION ====================
SHEET_ID = "1xSvsEPHV1MzHa9UumzJtyzAY4LXaiSVKb8tmMcUZPeM"

@st.cache_resource
def init_gsheet_connection():
    """Initialize Google Sheets connection"""
    try:
        # Lấy credentials từ Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )
        
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=60)  # Cache 1 phút
def load_data_from_sheets(_client):
    """Load all data from Google Sheets"""
    try:
        spreadsheet = _client.open_by_key(SHEET_ID)
        
        # Load revenue data
        try:
            revenue_sheet = spreadsheet.worksheet('revenue_monthly')
            revenue_records = revenue_sheet.get_all_records()
            if revenue_records:
                revenue_data = pd.DataFrame(revenue_records)
                revenue_data['Tháng'] = pd.to_datetime(revenue_data['Tháng'])
                revenue_data['Tổng DT'] = revenue_data['Nội bộ'] + revenue_data['Gov-Hiệp hội'] + revenue_data['Corporate']
            else:
                revenue_data = pd.DataFrame(columns=['Tháng', 'Nội bộ', 'Gov-Hiệp hội', 'Corporate', 'Tổng DT'])
        except:
            revenue_data = pd.DataFrame(columns=['Tháng', 'Nội bộ', 'Gov-Hiệp hội', 'Corporate', 'Tổng DT'])
        
        # Load pipeline data
        try:
            pipeline_sheet = spreadsheet.worksheet('sales_pipeline')
            pipeline_records = pipeline_sheet.get_all_records()
            pipeline_data = pd.DataFrame(pipeline_records) if pipeline_records else pd.DataFrame(columns=['Stage', 'Count', 'Value'])
        except:
            pipeline_data = pd.DataFrame(columns=['Stage', 'Count', 'Value'])
        
        # Load projects data
        try:
            projects_sheet = spreadsheet.worksheet('projects')
            projects_records = projects_sheet.get_all_records()
            projects = pd.DataFrame(projects_records) if projects_records else pd.DataFrame(columns=['Dự án', 'Doanh thu', 'Lợi nhuận %', 'Khách', 'Loại', 'CSAT'])
        except:
            projects = pd.DataFrame(columns=['Dự án', 'Doanh thu', 'Lợi nhuận %', 'Khách', 'Loại', 'CSAT'])
        
        # Load sales performance
        try:
            sales_sheet = spreadsheet.worksheet('sales_performance')
            sales_records = sales_sheet.get_all_records()
            sales_perf = pd.DataFrame(sales_records) if sales_records else pd.DataFrame(columns=['Nhân viên', 'Doanh thu', 'Số deal', 'Conversion %', 'Kênh'])
        except:
            sales_perf = pd.DataFrame(columns=['Nhân viên', 'Doanh thu', 'Số deal', 'Conversion %', 'Kênh'])
        
        return revenue_data, pipeline_data, projects, sales_perf
    
    except Exception as e:
        st.error(f"❌ Lỗi load dữ liệu: {str(e)}")
        return None, None, None, None

# ==================== MAIN APP ====================

# Sidebar
st.sidebar.title("📊 BEEVENT DASHBOARD")
st.sidebar.markdown("---")

# Connect to Google Sheets
client = init_gsheet_connection()

if client:
    with st.spinner("⏳ Đang tải dữ liệu từ Google Sheets..."):
        revenue_data, pipeline_data, projects, sales_perf = load_data_from_sheets(client)
    
    if revenue_data is not None:
        st.sidebar.success("✅ Kết nối Google Sheets thành công!")
        
        # Refresh button
        if st.sidebar.button("🔄 Làm mới dữ liệu"):
            st.cache_data.clear()
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Dashboard selection
        dashboard_type = st.sidebar.radio(
            "Chọn Dashboard:",
            ["🎯 CEO/CCO - Tổng quan", "💼 Kênh bán", "📋 Dự án", "📈 So sánh kế hoạch"]
        )
        
        st.sidebar.markdown("---")
        
        # Filters
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
            
            if len(revenue_data) > 0:
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
                    external_pct = ((revenue_data['Gov-Hiệp hội'].sum() + revenue_data['Corporate'].sum()) / revenue_data['Tổng DT'].sum() * 100)
                    st.metric(
                        "🎯 Khách ngoài",
                        f"{external_pct:.1f}%",
                        f"Target: 45%"
                    )
                
                with col4:
                    if len(pipeline_data) > 0:
                        pipeline_coverage = pipeline_data.iloc[0]['Value'] / (target_revenue / 12) if target_revenue > 0 else 0
                    else:
                        pipeline_coverage = 0
                    st.metric(
                        "📈 Pipeline Coverage",
                        f"{pipeline_coverage:.1f}x",
                        "Healthy" if pipeline_coverage >= 3 else "Warning"
                    )
            else:
                st.warning("⚠️ Chưa có dữ liệu doanh thu. Vui lòng nhập dữ liệu vào Google Sheet.")
            
            st.markdown("---")
            
            # Revenue Chart
            if len(revenue_data) > 0:
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.subheader("📊 Doanh thu theo kênh")
                    
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
                    
                    target_revenue = 80_000
                    fig_revenue.add_trace(go.Scatter(
                        name='Target tích lũy',
                        x=revenue_data['Tháng'],
                        y=[target_revenue/12 * (i+1) for i in range(len(revenue_data))],
                        mode='lines+markers',
                        line=dict(color='red', width=3, dash='dash')
                    ))
                    
                    fig_revenue.update_layout(
                        barmode='stack',
                        height=400,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig_revenue, use_container_width=True)
                
                with col2:
                    st.subheader("💧 Biên lợi nhuận")
                    
                    total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
                    cogs = total_revenue * 0.826
                    gross_profit = total_revenue * 0.174
                    operating_cost = gross_profit * 0.95
                    
                    fig_waterfall = go.Figure(go.Waterfall(
                        orientation="v",
                        measure=["relative", "relative", "total", "relative", "total"],
                        x=["Doanh thu", "COGS", "Lãi gộp", "Chi phí VH", "LNTT"],
                        y=[total_revenue, -cogs, 0, -operating_cost, 0],
                        text=[f"{total_revenue:,.0f}M", f"{-cogs:,.0f}M", f"{gross_profit:,.0f}M", 
                              f"{-operating_cost:,.0f}M", f"{gross_profit-operating_cost:,.0f}M"],
                        textposition="outside",
                        decreasing={"marker": {"color": "#ff6b6b"}},
                        increasing={"marker": {"color": "#51cf66"}},
                        totals={"marker": {"color": "#1f77b4"}}
                    ))
                    
                    fig_waterfall.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_waterfall, use_container_width=True)
            
            st.markdown("---")
            
            # Pipeline & Customer Mix
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Pipeline Coverage")
                
                if len(pipeline_data) > 0:
                    fig_funnel = go.Figure(go.Funnel(
                        y=pipeline_data['Stage'],
                        x=pipeline_data['Count'],
                        textposition="inside",
                        textinfo="value+percent initial",
                        marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
                    ))
                    
                    fig_funnel.update_layout(height=400)
                    st.plotly_chart(fig_funnel, use_container_width=True)
                    
                    conversion_rate = (pipeline_data.iloc[-1]['Count'] / pipeline_data.iloc[0]['Count']) * 100
                    st.info(f"📊 **Conversion Rate:** {conversion_rate:.1f}%")
                else:
                    st.warning("⚠️ Chưa có dữ liệu pipeline")
            
            with col2:
                st.subheader("🥧 Cơ cấu khách hàng")
                
                if len(revenue_data) > 0:
                    internal_pct = (revenue_data['Nội bộ'].sum() / revenue_data['Tổng DT'].sum() * 100)
                    external_pct = 100 - internal_pct
                    
                    fig_donut = go.Figure(data=[go.Pie(
                        labels=['Nội bộ', 'Bên ngoài'],
                        values=[internal_pct, external_pct],
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
                    
                    if abs(external_pct - 45) < 5:
                        st.success("✅ Đạt mục tiêu cơ cấu khách hàng")
                    else:
                        st.warning(f"⚠️ Chênh lệch: {external_pct - 45:+.1f}% so với target 45%")
                else:
                    st.info("Chưa có dữ liệu")
        
        # ==================== DASHBOARD 2: KÊNH BÁN ====================
        elif dashboard_type == "💼 Kênh bán":
            st.markdown('<div class="main-header">💼 DASHBOARD KÊNH BÁN</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_leads = pipeline_data.iloc[0]['Count'] if len(pipeline_data) > 0 else 0
                st.metric("🎯 Tổng Lead", f"{total_leads}")
            
            with col2:
                if len(pipeline_data) > 0:
                    win_rate = (pipeline_data.iloc[-1]['Count'] / pipeline_data.iloc[0]['Count'] * 100)
                    st.metric("✅ Win Rate", f"{win_rate:.1f}%")
                else:
                    st.metric("✅ Win Rate", "0%")
            
            with col3:
                if len(sales_perf) > 0:
                    avg_deal = sales_perf['Doanh thu'].sum() / sales_perf['Số deal'].sum()
                    st.metric("💵 AOV", f"{avg_deal/1000:.0f}M")
                else:
                    st.metric("💵 AOV", "0M")
            
            with col4:
                st.metric("⏱️ Avg. Close Time", "18 ngày")
            
            st.markdown("---")
            
            # Sales Performance
            st.subheader("🏆 Bảng xếp hạng Sales Performance")
            
            if len(sales_perf) > 0:
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    sales_perf_sorted = sales_perf.sort_values('Doanh thu', ascending=False).reset_index(drop=True)
                    sales_perf_sorted['Rank'] = range(1, len(sales_perf_sorted) + 1)
                    
                    display_df = sales_perf_sorted[['Rank', 'Nhân viên', 'Doanh thu', 'Số deal', 'Conversion %']].head(10).copy()
                    display_df['Doanh thu'] = display_df['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
                    
                    st.dataframe(display_df, hide_index=True, use_container_width=True, height=400)
                
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
                    
                    fig_scatter.update_layout(height=400)
                    st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("⚠️ Chưa có dữ liệu sales performance")
        
        # ==================== DASHBOARD 3: DỰ ÁN ====================
        elif dashboard_type == "📋 Dự án":
            st.markdown('<div class="main-header">📋 DASHBOARD DỰ ÁN</div>', unsafe_allow_html=True)
            
            if len(projects) > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📋 Tổng dự án", len(projects))
                
                with col2:
                    avg_profit = projects['Lợi nhuận %'].mean()
                    st.metric("💰 Biên LN TB", f"{avg_profit:.1f}%")
                
                with col3:
                    avg_csat = projects['CSAT'].mean()
                    st.metric("⭐ CSAT TB", f"{avg_csat:.2f}/5")
                
                with col4:
                    total_project_revenue = projects['Doanh thu'].sum() / 1_000_000
                    st.metric("💵 Tổng DT dự án", f"{total_project_revenue:,.0f}M")
                
                st.markdown("---")
                
                # Project Matrix
                st.subheader("💎 Ma trận Doanh thu - Lợi nhuận")
                
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
                
                # CSAT Analysis
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.subheader("⭐ Phân bố CSAT")
                    
                    csat_bins = pd.cut(projects['CSAT'], bins=[0, 3, 3.5, 4, 4.5, 5], 
                                      labels=['1-3', '3-3.5', '3.5-4', '4-4.5', '4.5-5'])
                    csat_dist = csat_bins.value_counts().sort_index()
                    
                    fig_csat = go.Figure(data=[go.Bar(
                        x=csat_dist.index.astype(str),
                        y=csat_dist.values,
                        marker_color=['#ff6b6b', '#ffa94d', '#ffd43b', '#51cf66', '#37b24d']
                    )])
                    
                    fig_csat.update_layout(height=300, xaxis_title="Điểm CSAT", yaxis_title="Số lượng")
                    st.plotly_chart(fig_csat, use_container_width=True)
                
                with col2:
                    st.subheader("📋 Dự án có CSAT thấp")
                    
                    low_csat = projects[projects['CSAT'] < 4.0][['Dự án', 'Loại', 'Doanh thu', 'CSAT']].sort_values('CSAT').copy()
                    
                    if len(low_csat) > 0:
                        low_csat['Doanh thu'] = low_csat['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
                        st.dataframe(low_csat, hide_index=True, use_container_width=True, height=300)
                    else:
                        st.success("🎉 Không có dự án nào có CSAT < 4.0!")
            else:
                st.warning("⚠️ Chưa có dữ liệu dự án")
        
        # ==================== DASHBOARD 4: SO SÁNH ====================
        else:
            st.markdown('<div class="main-header">📈 SO SÁNH KẾ HOẠCH VS THỰC TẾ</div>', unsafe_allow_html=True)
            
            if len(revenue_data) > 0:
                total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
                gross_profit = total_revenue * 0.174
                avg_csat = projects['CSAT'].mean() if len(projects) > 0 else 0
                
                comparison = pd.DataFrame({
                    'Chỉ tiêu': ['Doanh thu', 'Lãi gộp', 'LNTT', 'Số dự án', 'CSAT TB'],
                    'KH 2026': [80000, 13920, 82, 120, 4.2],
                    'TH hiện tại': [total_revenue, gross_profit, 45, len(projects), avg_csat],
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
                            ]
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
                    'KH tích lũy': [target_revenue/12 * (i+1) for i in range(len(revenue_data))],
                    'TH tích lũy': (revenue_data['Tổng DT'].cumsum() / 1_000_000).tolist()
                })
                
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=monthly_comparison['Tháng'],
                    y=monthly_comparison['KH tích lũy'],
                    mode='lines+markers',
                    name='Kế hoạch',
                    line=dict(color='red', width=3, dash='dash')
                ))
                
                fig_trend.add_trace(go.Scatter(
                    x=monthly_comparison['Tháng'],
                    y=monthly_comparison['TH tích lũy'],
                    mode='lines+markers',
                    name='Thực hiện',
                    line=dict(color='blue', width=3),
                    fill='tonexty',
                    fillcolor='rgba(31, 119, 180, 0.1)'
                ))
                
                fig_trend.update_layout(height=400, hovermode='x unified')
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning("⚠️ Chưa có dữ liệu")
    else:
        st.error("❌ Không thể load dữ liệu từ Google Sheets")
else:
    st.error("❌ Không thể kết nối Google Sheets. Kiểm tra secrets configuration.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Beevent Dashboard 2026</strong> | Powered by Streamlit & Google Sheets</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
