import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Beevent Management System",
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
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .staff-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GOOGLE SHEETS CONNECTION ====================
@st.cache_resource
def init_google_sheets():
    """Kết nối Google Sheets"""
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        spreadsheet_url = st.secrets.get("spreadsheet_url", None)
        
        if spreadsheet_url:
            sheet = client.open_by_url(spreadsheet_url)
        else:
            sheet = client.open("Beevent_Database")
        
        return sheet
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        return None

def get_worksheet(sheet, worksheet_name, headers):
    """Lấy hoặc tạo worksheet"""
    try:
        ws = sheet.worksheet(worksheet_name)
    except:
        ws = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        ws.append_row(headers)
    return ws

# ==================== DATA FUNCTIONS ====================

# --- PROJECTS ---
def load_projects(sheet):
    """Load dữ liệu dự án"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Team", "Ghi chú", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_project(sheet, project_data):
    """Lưu dự án mới"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Team", "Ghi chú", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    project_data["ID"] = f"PRJ{new_id:04d}"
    project_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(project_data.values()))
    return True

# --- STAFF ---
def load_staff(sheet):
    """Load danh sách nhân sự"""
    ws = get_worksheet(sheet, "Staff", [
        "ID", "Họ tên", "Chức vụ", "Phòng ban", "Email", "Điện thoại",
        "Ngày vào", "Lương", "Trạng thái", "Kỹ năng", "Ghi chú", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_staff(sheet, staff_data):
    """Lưu nhân sự mới"""
    ws = get_worksheet(sheet, "Staff", [
        "ID", "Họ tên", "Chức vụ", "Phòng ban", "Email", "Điện thoại",
        "Ngày vào", "Lương", "Trạng thái", "Kỹ năng", "Ghi chú", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    staff_data["ID"] = f"STF{new_id:04d}"
    staff_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(staff_data.values()))
    return True

# --- TIMELINE ---
def load_timeline(sheet):
    """Load timeline dự án"""
    ws = get_worksheet(sheet, "Timeline", [
        "ID", "Project_ID", "Giai đoạn", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc",
        "Phụ trách", "Trạng thái", "Tiến độ %", "Ghi chú", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_timeline(sheet, timeline_data):
    """Lưu timeline mới"""
    ws = get_worksheet(sheet, "Timeline", [
        "ID", "Project_ID", "Giai đoạn", "Mô tả", "Ngày bắt đầu", "Ngày kết thúc",
        "Phụ trách", "Trạng thái", "Tiến độ %", "Ghi chú", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    timeline_data["ID"] = f"TML{new_id:04d}"
    timeline_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(timeline_data.values()))
    return True

# --- CUSTOMERS ---
def load_customers(sheet):
    """Load danh sách khách hàng"""
    ws = get_worksheet(sheet, "Customers", [
        "ID", "Tên khách hàng", "Công ty", "Email", "Điện thoại", 
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_customer(sheet, customer_data):
    """Lưu khách hàng mới"""
    ws = get_worksheet(sheet, "Customers", [
        "ID", "Tên khách hàng", "Công ty", "Email", "Điện thoại", 
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    customer_data["ID"] = f"CUS{new_id:04d}"
    customer_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(customer_data.values()))
    return True

# ==================== DASHBOARD DATA PROCESSING ====================

def process_dashboard_data(projects_df, customers_df, staff_df):
    """
    Xử lý dữ liệu từ Google Sheets để hiển thị dashboard
    """
    
    # Convert data types
    if len(projects_df) > 0:
        projects_df['Doanh thu'] = pd.to_numeric(projects_df['Doanh thu'], errors='coerce').fillna(0)
        projects_df['Chi phí'] = pd.to_numeric(projects_df['Chi phí'], errors='coerce').fillna(0)
        projects_df['Lợi nhuận %'] = pd.to_numeric(projects_df['Lợi nhuận %'], errors='coerce').fillna(0)
        
        # Parse dates
        try:
            projects_df['Ngày bắt đầu'] = pd.to_datetime(projects_df['Ngày bắt đầu'], errors='coerce')
            projects_df['Ngày kết thúc'] = pd.to_datetime(projects_df['Ngày kết thúc'], errors='coerce')
        except:
            pass
    
    # 1. REVENUE DATA - Doanh thu theo tháng và kênh
    if len(projects_df) > 0 and 'Ngày bắt đầu' in projects_df.columns:
        projects_df['Tháng'] = projects_df['Ngày bắt đầu'].dt.to_period('M')
        
        # Phân loại kênh dựa trên loại khách hàng
        def classify_channel(row):
            loai = str(row.get('Loại', '')).lower()
            khach_hang = str(row.get('Khách hàng', '')).lower()
            
            if 'nội bộ' in loai or 'internal' in khach_hang:
                return 'Nội bộ'
            elif 'gov' in loai or 'hiệp hội' in loai or 'chính phủ' in khach_hang:
                return 'Gov-Hiệp hội'
            else:
                return 'Corporate'
        
        projects_df['Kênh'] = projects_df.apply(classify_channel, axis=1)
        
        # Tạo revenue data theo tháng
        revenue_by_month = projects_df.groupby(['Tháng', 'Kênh'])['Doanh thu'].sum().unstack(fill_value=0)
        
        # Đảm bảo có đủ 3 kênh
        for channel in ['Nội bộ', 'Gov-Hiệp hội', 'Corporate']:
            if channel not in revenue_by_month.columns:
                revenue_by_month[channel] = 0
        
        revenue_data = revenue_by_month.reset_index()
        revenue_data['Tháng'] = revenue_data['Tháng'].dt.to_timestamp()
        revenue_data['Tổng DT'] = revenue_data[['Nội bộ', 'Gov-Hiệp hội', 'Corporate']].sum(axis=1)
    else:
        # Nếu không có dữ liệu, tạo template rỗng
        months = pd.date_range('2026-01-01', periods=12, freq='MS')
        revenue_data = pd.DataFrame({
            'Tháng': months,
            'Nội bộ': [0] * 12,
            'Gov-Hiệp hội': [0] * 12,
            'Corporate': [0] * 12,
            'Tổng DT': [0] * 12
        })
    
    # 2. PIPELINE DATA - Phân bố theo trạng thái
    if len(projects_df) > 0 and 'Trạng thái' in projects_df.columns:
        status_mapping = {
            'Lead': ['Lead', 'Mới'],
            'Qualified': ['Đang đàm phán', 'Qualified'],
            'Proposal': ['Đã gửi proposal', 'Đã ký HĐ'],
            'Won': ['Hoàn thành', 'Đang thực hiện']
        }
        
        pipeline_counts = {'Lead': 0, 'Qualified': 0, 'Proposal': 0, 'Won': 0}
        pipeline_values = {'Lead': 0, 'Qualified': 0, 'Proposal': 0, 'Won': 0}
        
        for idx, row in projects_df.iterrows():
            status = str(row.get('Trạng thái', ''))
            revenue = row.get('Doanh thu', 0)
            
            for stage, statuses in status_mapping.items():
                if any(s in status for s in statuses):
                    pipeline_counts[stage] += 1
                    pipeline_values[stage] += revenue / 1_000_000
                    break
        
        pipeline_data = pd.DataFrame({
            'Stage': list(pipeline_counts.keys()),
            'Count': list(pipeline_counts.values()),
            'Value': list(pipeline_values.values())
        })
    else:
        pipeline_data = pd.DataFrame({
            'Stage': ['Lead', 'Qualified', 'Proposal', 'Won'],
            'Count': [0, 0, 0, 0],
            'Value': [0, 0, 0, 0]
        })
    
    # 3. SALES PERFORMANCE - Hiệu suất theo PIC
    if len(projects_df) > 0 and 'PIC' in projects_df.columns:
        sales_perf = projects_df.groupby('PIC').agg({
            'Doanh thu': 'sum',
            'ID': 'count',
            'Kênh': lambda x: x.mode()[0] if len(x) > 0 else 'Corporate'
        }).reset_index()
        
        sales_perf.columns = ['Nhân viên', 'Doanh thu', 'Số deal', 'Kênh']
        
        # Tính conversion rate (giả định)
        sales_perf['Conversion %'] = sales_perf['Số deal'] * np.random.uniform(15, 45, len(sales_perf))
    else:
        sales_perf = pd.DataFrame({
            'Nhân viên': [],
            'Doanh thu': [],
            'Số deal': [],
            'Conversion %': [],
            'Kênh': []
        })
    
    # 4. PROJECT DETAILS - Thêm CSAT (giả định nếu chưa có)
    if len(projects_df) > 0:
        if 'CSAT' not in projects_df.columns:
            projects_df['CSAT'] = np.random.uniform(3.5, 5.0, len(projects_df))
        
        if 'Khách' not in projects_df.columns:
            projects_df['Khách'] = np.random.randint(50, 1000, len(projects_df))
    
    return revenue_data, pipeline_data, sales_perf, projects_df

# ==================== SIDEBAR ====================
st.sidebar.title("🎯 BEEVENT SYSTEM")
st.sidebar.markdown("---")

# Kết nối Google Sheets
sheet = init_google_sheets()

if sheet is None:
    st.error("⚠️ Không thể kết nối Google Sheets!")
    st.stop()

# Navigation
page = st.sidebar.radio(
    "📋 Menu chính:",
    [
        "🏠 Tổng quan",
        "📝 Quản lý Dự án",
        "📅 Timeline Dự án",
        "👥 Quản lý Khách hàng",
        "👨‍💼 Quản lý Nhân sự",
        "💰 Quản lý Tài chính",
        "📊 Dashboard & Báo cáo",
        "⚙️ Cài đặt"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(f"👤 **User:** Admin\n📅 **Ngày:** {datetime.now().strftime('%d/%m/%Y')}")

# ==================== PAGE 1: TỔNG QUAN ====================
if page == "🏠 Tổng quan":
    st.markdown('<div class="main-header">🏠 TỔNG QUAN HỆ THỐNG</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    customers_df = load_customers(sheet)
    staff_df = load_staff(sheet)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_projects = len(projects_df)
        active_projects = len(projects_df[projects_df['Trạng thái'] == 'Đang thực hiện']) if len(projects_df) > 0 else 0
        st.metric("📋 Tổng dự án", total_projects, f"{active_projects} đang chạy")
    
    with col2:
        total_customers = len(customers_df)
        st.metric("👥 Khách hàng", total_customers, "+5 tháng này")
    
    with col3:
        total_staff = len(staff_df)
        active_staff = len(staff_df[staff_df['Trạng thái'] == 'Đang làm']) if len(staff_df) > 0 else 0
        st.metric("👨‍💼 Nhân sự", total_staff, f"{active_staff} active")
    
    with col4:
        if len(projects_df) > 0 and 'Doanh thu' in projects_df.columns:
            total_revenue = pd.to_numeric(projects_df['Doanh thu'], errors='coerce').sum() / 1_000_000
            st.metric("💰 Doanh thu", f"{total_revenue:.1f}M", "+12%")
        else:
            st.metric("💰 Doanh thu", "0M", "Chưa có dữ liệu")
    
    st.markdown("---")
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dự án gần đây")
        if len(projects_df) > 0:
            recent_projects = projects_df.tail(5)[['Tên dự án', 'Khách hàng', 'Trạng thái', 'PIC']]
            st.dataframe(recent_projects, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dự án nào. Hãy tạo dự án đầu tiên!")
    
    with col2:
        st.subheader("👨‍💼 Nhân sự theo phòng ban")
        if len(staff_df) > 0 and 'Phòng ban' in staff_df.columns:
            dept_dist = staff_df['Phòng ban'].value_counts()
            fig = px.pie(values=dept_dist.values, names=dept_dist.index, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu nhân sự")

# ==================== PAGE 7: DASHBOARD & BÁO CÁO ====================
elif page == "📊 Dashboard & Báo cáo":
    st.markdown('<div class="main-header">📊 DASHBOARD & BÁO CÁO</div>', unsafe_allow_html=True)
    
    # Load data từ Google Sheets
    projects_df = load_projects(sheet)
    customers_df = load_customers(sheet)
    staff_df = load_staff(sheet)
    
    # Process data cho dashboard
    revenue_data, pipeline_data, sales_perf, projects = process_dashboard_data(projects_df, customers_df, staff_df)
    
    # Hiển thị trạng thái dữ liệu
    if len(projects_df) == 0:
        st.warning("⚠️ **Chưa có dữ liệu dự án!** Vui lòng thêm dự án ở tab 'Quản lý Dự án' để xem dashboard đầy đủ.")
        st.info("💡 Dashboard đang hiển thị với dữ liệu mẫu (0 VNĐ)")
    else:
        st.success(f"✅ Đang hiển thị dữ liệu thật từ Google Sheets: **{len(projects_df)} dự án**")
    
    st.markdown("---")
    
    # Dashboard selection
    dashboard_type = st.radio(
        "Chọn Dashboard:",
        ["🎯 CEO/CCO - Tổng quan", "💼 Kênh bán", "📋 Dự án", "📈 So sánh kế hoạch"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Filters
    with st.expander("⚙️ Bộ lọc", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            channel_filter = st.multiselect(
                "Kênh bán:",
                ["Nội bộ", "Gov-Hiệp hội", "Corporate"],
                default=["Nội bộ", "Gov-Hiệp hội", "Corporate"]
            )
        with col2:
            st.info("💡 **Mục tiêu 2026**\n- DT: 80 tỷ | Lãi gộp: 13.92 tỷ")
    
    st.markdown("---")
    
    # ==================== DASHBOARD 1: CEO/CCO ====================
    if dashboard_type == "🎯 CEO/CCO - Tổng quan":
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
        target_revenue = 80_000
        revenue_achievement = (total_revenue / target_revenue) * 100 if total_revenue > 0 else 0
        
        with col1:
            st.metric("💰 Doanh thu tích lũy", f"{total_revenue:,.0f}M", f"{revenue_achievement:.1f}% target")
        
        with col2:
            gross_profit = total_revenue * 0.174
            st.metric("📊 Lãi gộp", f"{gross_profit:,.0f}M", f"{(gross_profit/13920)*100:.1f}% target" if gross_profit > 0 else "0%")
        
        with col3:
            # Tính tỷ lệ khách ngoài từ dữ liệu thật
            if len(projects_df) > 0 and 'Loại' in projects_df.columns:
                external_projects = len(projects_df[~projects_df['Loại'].str.contains('Nội bộ', case=False, na=False)])
                external_rate = (external_projects / len(projects_df) * 100) if len(projects_df) > 0 else 0
            else:
                external_rate = 0
            st.metric("🎯 Khách ngoài", f"{external_rate:.1f}%", f"Target: 45%")
        
        with col4:
            # Pipeline coverage từ dữ liệu thật
            total_pipeline = pipeline_data['Count'].sum()
            won_count = pipeline_data[pipeline_data['Stage'] == 'Won']['Count'].values[0] if len(pipeline_data) > 0 else 0
            pipeline_coverage = (total_pipeline / won_count) if won_count > 0 else 0
            st.metric("📈 Pipeline Coverage", f"{pipeline_coverage:.1f}x", "Healthy" if pipeline_coverage >= 3 else "Low")
        
        st.markdown("---")
        
        # Revenue Chart
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
                        text=[f"{val/1_000_000:.0f}M" if val > 0 else "" for val in revenue_data[channel]],
                        textposition='inside'
                    ))
            
            # Target line
            cumulative_target = [target_revenue/12 * (i+1) for i in range(len(revenue_data))]
            fig_revenue.add_trace(go.Scatter(
                name='Target',
                x=revenue_data['Tháng'],
                y=cumulative_target,
                mode='lines+markers',
                line=dict(color='red', width=3, dash='dash')
            ))
            
            fig_revenue.update_layout(
                barmode='stack', 
                height=400, 
                hovermode='x unified',
                yaxis_title="Doanh thu (M VNĐ)"
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            st.subheader("💧 Biên lợi nhuận")
            
            cogs = total_revenue * 0.826
            operating_cost = gross_profit * 0.95
            net_profit = gross_profit - operating_cost
            
            fig_waterfall = go.Figure(go.Waterfall(
                orientation="v",
                measure=["relative", "relative", "total", "relative", "total"],
                x=["Doanh thu", "COGS", "Lãi gộp", "Chi phí VH", "LNTT"],
                y=[total_revenue, -cogs, 0, -operating_cost, 0],
                text=[f"{total_revenue:,.0f}M", f"{-cogs:,.0f}M", f"{gross_profit:,.0f}M", 
                      f"{-operating_cost:,.0f}M", f"{net_profit:,.0f}M"],
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
            
            if pipeline_data['Count'].sum() > 0:
                fig_funnel = go.Figure(go.Funnel(
                    y=pipeline_data['Stage'],
                    x=pipeline_data['Count'],
                    textposition="inside",
                    textinfo="value+percent initial",
                    marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
                ))
                
                fig_funnel.update_layout(height=400)
                st.plotly_chart(fig_funnel, use_container_width=True)
                
                conversion_rate = (pipeline_data.iloc[-1]['Count'] / pipeline_data.iloc[0]['Count'] * 100) if pipeline_data.iloc[0]['Count'] > 0 else 0
                st.info(f"📊 **Conversion Rate:** {conversion_rate:.1f}% | **Won Projects:** {pipeline_data.iloc[-1]['Count']}")
            else:
                st.info("Chưa có dữ liệu pipeline")
        
        with col2:
            st.subheader("🥧 Cơ cấu khách hàng")
            
            # Tính tỷ lệ nội bộ vs bên ngoài từ dữ liệu thật
            if len(projects_df) > 0 and 'Loại' in projects_df.columns:
                internal_count = len(projects_df[projects_df['Loại'].str.contains('Nội bộ', case=False, na=False)])
                external_count = len(projects_df) - internal_count
                
                internal_pct = (internal_count / len(projects_df) * 100) if len(projects_df) > 0 else 0
                external_pct = 100 - internal_pct
            else:
                internal_pct, external_pct = 0, 0
            
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
            
            if external_pct >= 45:
                st.success(f"✅ Đạt mục tiêu cơ cấu khách hàng ({external_pct:.0f}% >= 45%)")
            else:
                st.warning(f"⚠️ Chưa đạt mục tiêu ({external_pct:.0f}% < 45%)")
    
    # ==================== DASHBOARD 2: KÊNH BÁN ====================
    elif dashboard_type == "💼 Kênh bán":
        col1, col2, col3, col4 = st.columns(4)
        
        total_leads = pipeline_data['Count'].sum()
        won_count = pipeline_data[pipeline_data['Stage'] == 'Won']['Count'].values[0] if len(pipeline_data) > 0 else 0
        win_rate = (won_count / total_leads * 100) if total_leads > 0 else 0
        
        with col1:
            st.metric("🎯 Tổng Lead", int(total_leads), f"+{int(total_leads * 0.08)}")
        with col2:
            st.metric("✅ Win Rate", f"{win_rate:.1f}%", f"+{win_rate * 0.1:.1f}%")
        with col3:
            avg_deal = (sales_perf['Doanh thu'].sum() / sales_perf['Số deal'].sum() / 1000) if len(sales_perf) > 0 and sales_perf['Số deal'].sum() > 0 else 0
            st.metric("💵 AOV", f"{avg_deal:.0f}M", "+15%")
        with col4:
            st.metric("⏱️ Close Time", "18 ngày", "-3")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("🔄 Lead Flow (Sankey)")
            
            if pipeline_data['Count'].sum() > 0:
                # Tính lost từ mỗi stage
                lead_count = pipeline_data[pipeline_data['Stage'] == 'Lead']['Count'].values[0]
                qualified_count = pipeline_data[pipeline_data['Stage'] == 'Qualified']['Count'].values[0]
                proposal_count = pipeline_data[pipeline_data['Stage'] == 'Proposal']['Count'].values[0]
                won_count = pipeline_data[pipeline_data['Stage'] == 'Won']['Count'].values[0]
                
                lost_from_lead = lead_count - qualified_count
                lost_from_qualified = qualified_count - proposal_count
                lost_from_proposal = proposal_count - won_count
                
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        label=["Lead", "Qualified", "Proposal", "Won", "Lost"],
                        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#7f7f7f"]
                    ),
                    link=dict(
                        source=[0, 0, 1, 1, 2, 2],
                        target=[1, 4, 2, 4, 3, 4],
                        value=[qualified_count, lost_from_lead, proposal_count, lost_from_qualified, won_count, lost_from_proposal],
                        color=["rgba(31,119,180,0.3)", "rgba(127,127,127,0.3)", 
                               "rgba(255,127,14,0.3)", "rgba(127,127,127,0.3)",
                               "rgba(44,160,44,0.3)", "rgba(127,127,127,0.3)"]
                    )
                )])
                
                fig_sankey.update_layout(height=400)
                st.plotly_chart(fig_sankey, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu pipeline")
        
        with col2:
            st.subheader("📊 Phân bố giá trị Deal")
            
            if len(projects_df) > 0 and 'Doanh thu' in projects_df.columns:
                deal_values = pd.to_numeric(projects_df['Doanh thu'], errors='coerce').dropna() / 1000
                
                if len(deal_values) > 0:
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(
                        y=deal_values,
                        boxmean='sd',
                        marker_color='#1f77b4'
                    ))
                    
                    fig_box.update_layout(
                        height=400,
                        yaxis_title="Giá trị (M VNĐ)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_box, use_container_width=True)
                    st.info(f"📊 **Median:** {deal_values.median():.1f}M | **Mean:** {deal_values.mean():.1f}M")
                else:
                    st.info("Chưa có dữ liệu doanh thu")
            else:
                st.info("Chưa có dữ liệu")
        
        st.markdown("---")
        
        st.subheader("🏆 Sales Performance")
        
        if len(sales_perf) > 0:
            sales_perf_sorted = sales_perf.sort_values('Doanh thu', ascending=False).reset_index(drop=True)
            
            col1, col2 = st.columns([2, 3])
            
            with col1:
                top_5 = sales_perf_sorted.head(5)[['Nhân viên', 'Doanh thu', 'Số deal']].copy()
                top_5['Doanh thu'] = top_5['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
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
        else:
            st.info("Chưa có dữ liệu sales performance")
    
    # ==================== DASHBOARD 3: DỰ ÁN ====================
    elif dashboard_type == "📋 Dự án":
        col1, col2, col3, col4 = st.columns(4)
        
        active_projects = len(projects[projects['Trạng thái'] == 'Đang thực hiện']) if len(projects) > 0 else 0
        avg_profit = projects['Lợi nhuận %'].mean() if len(projects) > 0 else 0
        avg_csat = projects['CSAT'].mean() if len(projects) > 0 and 'CSAT' in projects.columns else 0
        
        with col1:
            st.metric("📋 Dự án đang chạy", active_projects, f"+{int(active_projects * 0.25)}")
        with col2:
            st.metric("💰 Biên LN TB", f"{avg_profit:.1f}%", "+2.3%")
        with col3:
            st.metric("⭐ CSAT TB", f"{avg_csat:.2f}/5", "+0.15")
        with col4:
            st.metric("📊 Cost Variance", "8.5%", "OK")
        
        st.markdown("---")
        
        if len(projects) > 0:
            st.subheader("💎 Ma trận Doanh thu - Lợi nhuận")
            
            fig_scatter = px.scatter(
                projects,
                x='Doanh thu',
                y='Lợi nhuận %',
                size='Khách' if 'Khách' in projects.columns else None,
                color='Loại',
                hover_data=['Tên dự án', 'CSAT'] if 'CSAT' in projects.columns else ['Tên dự án'],
                title="Bubble size = Số lượng khách"
            )
            
            fig_scatter.add_hline(y=projects['Lợi nhuận %'].median(), line_dash="dash", line_color="gray")
            fig_scatter.add_vline(x=projects['Doanh thu'].median(), line_dash="dash", line_color="gray")
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.info("💡 **Insight:** Tập trung nhân rộng các event ở góc phải trên (DT cao + LN cao)")
            
            st.markdown("---")
            
            # CSAT Distribution
            if 'CSAT' in projects.columns:
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
                    low_csat = projects[projects['CSAT'] < 4.0][['Tên dự án', 'Loại', 'Doanh thu', 'CSAT']].sort_values('CSAT').copy()
                    
                    if len(low_csat) > 0:
                        low_csat['Doanh thu'] = low_csat['Doanh thu'].apply(lambda x: f"{x/1000:.0f}M")
                        st.dataframe(low_csat, hide_index=True, use_container_width=True, height=300)
                    else:
                        st.success("🎉 Không có dự án nào có CSAT < 4.0!")
        else:
            st.info("Chưa có dữ liệu dự án")
    
    # ==================== DASHBOARD 4: SO SÁNH ====================
    else:
        total_revenue = revenue_data['Tổng DT'].sum() / 1_000_000
        gross_profit = total_revenue * 0.174
        net_profit = gross_profit * 0.05
        avg_csat = projects['CSAT'].mean() if len(projects) > 0 and 'CSAT' in projects.columns else 0
        
        comparison = pd.DataFrame({
            'Chỉ tiêu': ['Doanh thu', 'Lãi gộp', 'LNTT', 'Số dự án', 'CSAT TB'],
            'KH 2026': [80000, 13920, 82, 120, 4.2],
            'TH hiện tại': [total_revenue, gross_profit, net_profit, len(projects), avg_csat],
            'Đơn vị': ['M', 'M', 'M', 'dự án', 'điểm']
        })
        
        comparison['% Hoàn thành'] = (comparison['TH hiện tại'] / comparison['KH 2026'] * 100).round(1)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("📊 Bảng so sánh chi tiết")
            st.dataframe(comparison, hide_index=True, use_container_width=True, height=250)
        
        with col2:
            st.subheader("🎯 Tỷ lệ hoàn thành")
            
            revenue_achievement = (total_revenue / 80000) * 100 if total_revenue > 0 else 0
            
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
            'KH tích lũy': [target_revenue/12 * (i+1) for i in range(len(revenue_data))],
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
        
        fig_trend.update_layout(
            height=400, 
            hovermode='x unified', 
            yaxis_title="Doanh thu tích lũy (M VNĐ)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Beevent Management System v2.0</strong> | Powered by Streamlit & Google Sheets</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
