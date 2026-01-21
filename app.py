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
    .timeline-item {
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
        margin-bottom: 1rem;
        position: relative;
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

def update_project(sheet, project_id, updated_data):
    """Cập nhật dự án"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Team", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == project_id:
            for col_idx, (key, value) in enumerate(updated_data.items(), start=1):
                ws.update_cell(idx, col_idx, value)
            return True
    return False

def delete_project(sheet, project_id):
    """Xóa dự án"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Team", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == project_id:
            ws.delete_rows(idx)
            return True
    return False

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

def update_staff(sheet, staff_id, updated_data):
    """Cập nhật nhân sự"""
    ws = get_worksheet(sheet, "Staff", [
        "ID", "Họ tên", "Chức vụ", "Phòng ban", "Email", "Điện thoại",
        "Ngày vào", "Lương", "Trạng thái", "Kỹ năng", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == staff_id:
            for col_idx, (key, value) in enumerate(updated_data.items(), start=1):
                ws.update_cell(idx, col_idx, value)
            return True
    return False

def delete_staff(sheet, staff_id):
    """Xóa nhân sự"""
    ws = get_worksheet(sheet, "Staff", [
        "ID", "Họ tên", "Chức vụ", "Phòng ban", "Email", "Điện thoại",
        "Ngày vào", "Lương", "Trạng thái", "Kỹ năng", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == staff_id:
            ws.delete_rows(idx)
            return True
    return False

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
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_customer(sheet, customer_data):
    """Lưu khách hàng mới"""
    ws = get_worksheet(sheet, "Customers", [
        "ID", "Tên khách hàng", "Công ty", "Email", "Điện thoại", 
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    customer_data["ID"] = f"CUS{new_id:04d}"
    customer_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(customer_data.values()))
    return True

def update_customer(sheet, customer_id, updated_data):
    """Cập nhật khách hàng"""
    ws = get_worksheet(sheet, "Customers", [
        "ID", "Tên khách hàng", "Công ty", "Email", "Điện thoại", 
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == customer_id:
            for col_idx, (key, value) in enumerate(updated_data.items(), start=1):
                ws.update_cell(idx, col_idx, value)
            return True
    return False

def delete_customer(sheet, customer_id):
    """Xóa khách hàng"""
    ws = get_worksheet(sheet, "Customers", [
        "ID", "Tên khách hàng", "Công ty", "Email", "Điện thoại", 
        "Địa chỉ", "Loại", "Nguồn", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    all_records = ws.get_all_records()
    for idx, record in enumerate(all_records, start=2):
        if record['ID'] == customer_id:
            ws.delete_rows(idx)
            return True
    return False

# --- FINANCE ---
def load_finance(sheet):
    """Load dữ liệu tài chính"""
    ws = get_worksheet(sheet, "Finance", [
        "ID", "Project_ID", "Loại", "Hạng mục", "Số tiền", "Ngày", 
        "Người thanh toán", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_finance(sheet, finance_data):
    """Lưu giao dịch tài chính"""
    ws = get_worksheet(sheet, "Finance", [
        "ID", "Project_ID", "Loại", "Hạng mục", "Số tiền", "Ngày", 
        "Người thanh toán", "Trạng thái", "Ghi chú", "Ngày tạo"
    ])
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    finance_data["ID"] = f"FIN{new_id:04d}"
    finance_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row(list(finance_data.values()))
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

# ==================== PAGE 2: QUẢN LÝ DỰ ÁN ====================
elif page == "📝 Quản lý Dự án":
    st.markdown('<div class="main-header">📝 QUẢN LÝ DỰ ÁN</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "📊 Thống kê"])
    
    # TAB 1: Danh sách dự án
    with tab1:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Lọc theo trạng thái:",
                    options=projects_df['Trạng thái'].unique().tolist(),
                    default=projects_df['Trạng thái'].unique().tolist()
                )
            
            with col2:
                if 'Loại' in projects_df.columns:
                    type_filter = st.multiselect(
                        "Lọc theo loại:",
                        options=projects_df['Loại'].unique().tolist(),
                        default=projects_df['Loại'].unique().tolist()
                    )
                else:
                    type_filter = []
            
            with col3:
                search_term = st.text_input("🔍 Tìm kiếm:", placeholder="Tên dự án, khách hàng...")
            
            # Apply filters
            filtered_df = projects_df[projects_df['Trạng thái'].isin(status_filter)]
            
            if type_filter and 'Loại' in projects_df.columns:
                filtered_df = filtered_df[filtered_df['Loại'].isin(type_filter)]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Tên dự án'].str.contains(search_term, case=False, na=False) |
                    filtered_df['Khách hàng'].str.contains(search_term, case=False, na=False)
                ]
            
            st.markdown(f"**Tìm thấy {len(filtered_df)} dự án**")
            
            # Display projects
            for idx, row in filtered_df.iterrows():
                with st.expander(f"🎯 {row['Tên dự án']} - {row['Khách hàng']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID:** {row['ID']}")
                        st.write(f"**Loại:** {row.get('Loại', 'N/A')}")
                        st.write(f"**Trạng thái:** {row['Trạng thái']}")
                    
                    with col2:
                        st.write(f"**Ngày bắt đầu:** {row.get('Ngày bắt đầu', 'N/A')}")
                        st.write(f"**Ngày kết thúc:** {row.get('Ngày kết thúc', 'N/A')}")
                        st.write(f"**PIC:** {row.get('PIC', 'N/A')}")
                    
                    with col3:
                        doanh_thu = pd.to_numeric(row.get('Doanh thu', 0), errors='coerce')
                        chi_phi = pd.to_numeric(row.get('Chi phí', 0), errors='coerce')
                        st.write(f"**Doanh thu:** {doanh_thu:,.0f} VNĐ")
                        st.write(f"**Chi phí:** {chi_phi:,.0f} VNĐ")
                        st.write(f"**Lợi nhuận:** {row.get('Lợi nhuận %', 0)}%")
                    
                    st.write(f"**Ghi chú:** {row.get('Ghi chú', 'Không có')}")
                    
                    # Actions
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button("✏️ Sửa", key=f"edit_{row['ID']}"):
                            st.session_state[f'editing_{row["ID"]}'] = True
                    with col2:
                        if st.button("🗑️ Xóa", key=f"delete_{row['ID']}"):
                            if delete_project(sheet, row['ID']):
                                st.success("Đã xóa dự án!")
                                st.rerun()
        else:
            st.info("📭 Chưa có dự án nào. Hãy thêm dự án đầu tiên!")
    
    # TAB 2: Thêm dự án mới
    with tab2:
        st.subheader("➕ Thêm dự án mới")
        
        with st.form("add_project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                ten_du_an = st.text_input("Tên dự án *", placeholder="Ví dụ: Year End Party 2026")
                khach_hang = st.text_input("Khách hàng *", placeholder="Tên công ty/tổ chức")
                loai = st.selectbox("Loại dự án *", ["Teambuilding", "Gala Dinner", "Conference", "Festival", "Workshop", "Nội bộ", "Gov", "Corporate"])
                ngay_bat_dau = st.date_input("Ngày bắt đầu *")
                ngay_ket_thuc = st.date_input("Ngày kết thúc *")
            
            with col2:
                doanh_thu = st.number_input("Doanh thu (VNĐ) *", min_value=0, step=1000000, format="%d")
                chi_phi = st.number_input("Chi phí (VNĐ) *", min_value=0, step=1000000, format="%d")
                loi_nhuan = ((doanh_thu - chi_phi) / doanh_thu * 100) if doanh_thu > 0 else 0
                st.metric("Lợi nhuận %", f"{loi_nhuan:.2f}%")
                trang_thai = st.selectbox("Trạng thái *", ["Lead", "Đang đàm phán", "Đã ký HĐ", "Đang thực hiện", "Hoàn thành", "Hủy"])
                pic = st.text_input("PIC (Người phụ trách)", placeholder="Nguyễn Văn A")
            
            team = st.text_input("Team", placeholder="Ví dụ: Team A, Team B")
            ghi_chu = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu dự án", use_container_width=True)
            
            if submitted:
                if not ten_du_an or not khach_hang:
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    project_data = {
                        "ID": "",  # Will be auto-generated
                        "Tên dự án": ten_du_an,
                        "Khách hàng": khach_hang,
                        "Loại": loai,
                        "Ngày bắt đầu": ngay_bat_dau.strftime("%Y-%m-%d"),
                        "Ngày kết thúc": ngay_ket_thuc.strftime("%Y-%m-%d"),
                        "Doanh thu": doanh_thu,
                        "Chi phí": chi_phi,
                        "Lợi nhuận %": round(loi_nhuan, 2),
                        "Trạng thái": trang_thai,
                        "PIC": pic,
                        "Team": team,
                        "Ghi chú": ghi_chu,
                        "Ngày tạo": ""  # Will be auto-generated
                    }
                    
                    if save_project(sheet, project_data):
                        st.success("✅ Đã thêm dự án thành công!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Có lỗi xảy ra. Vui lòng thử lại!")
    
    # TAB 3: Thống kê
    with tab3:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_revenue = pd.to_numeric(projects_df['Doanh thu'], errors='coerce').sum()
                st.metric("💰 Tổng doanh thu", f"{total_revenue/1_000_000:,.1f}M VNĐ")
            
            with col2:
                total_cost = pd.to_numeric(projects_df['Chi phí'], errors='coerce').sum()
                st.metric("💸 Tổng chi phí", f"{total_cost/1_000_000:,.1f}M VNĐ")
            
            with col3:
                avg_profit = pd.to_numeric(projects_df['Lợi nhuận %'], errors='coerce').mean()
                st.metric("📊 Lợi nhuận TB", f"{avg_profit:.1f}%")
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Dự án theo trạng thái")
                status_dist = projects_df['Trạng thái'].value_counts()
                fig = px.pie(values=status_dist.values, names=status_dist.index)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Doanh thu theo loại")
                if 'Loại' in projects_df.columns:
                    revenue_by_type = projects_df.groupby('Loại')['Doanh thu'].sum().sort_values(ascending=False)
                    fig = px.bar(x=revenue_by_type.index, y=revenue_by_type.values/1_000_000)
                    fig.update_layout(xaxis_title="Loại dự án", yaxis_title="Doanh thu (M VNĐ)")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu để thống kê")

# ==================== PAGE 3: TIMELINE DỰ ÁN ====================
# ==================== PAGE 3: TIMELINE DỰ ÁN (FULL FEATURES) ====================
elif page == "📅 Timeline Dự án":
    st.markdown('<div class="main-header">📅 SƠ ĐỒ GANTT</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    timeline_df = load_timeline(sheet)
    members_df = load_members(sheet)  # Load danh sách nhân sự
    
    tab1, tab2 = st.tabs(["📊 Gantt Chart", "➕ Thêm giai đoạn"])
    
    # TAB 1: CALENDAR GANTT CHART
    with tab1:
        if len(projects_df) > 0:
            # Month navigation
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if 'current_month' not in st.session_state:
                    st.session_state.current_month = datetime.now()
                
                if st.button("◀️ Tháng trước", use_container_width=True):
                    st.session_state.current_month = st.session_state.current_month - timedelta(days=30)
                    st.rerun()
            
            with col2:
                current_month = st.session_state.current_month
                st.markdown(f"<h3 style='text-align: center;'>📅 Tháng {current_month.month} năm {current_month.year}</h3>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Tháng sau ▶️", use_container_width=True):
                    st.session_state.current_month = st.session_state.current_month + timedelta(days=30)
                    st.rerun()
            
            # Project filter
            col1, col2 = st.columns([4, 1])
            
            with col1:
                selected_project = st.selectbox(
                    "Chọn dự án:",
                    options=['Tất cả'] + projects_df['ID'].tolist(),
                    format_func=lambda x: f"Tất cả dự án" if x == 'Tất cả' else f"{x} - {projects_df[projects_df['ID']==x]['Tên dự án'].values[0]}"
                )
            
            with col2:
                st.text("")
                st.text("")
                if st.button("🔄 Làm mới", use_container_width=True):
                    st.rerun()
            
            st.markdown("---")
            
            # Filter timeline
            if selected_project == 'Tất cả':
                filtered_timeline = timeline_df.copy()
            else:
                filtered_timeline = timeline_df[timeline_df['Project_ID'] == selected_project].copy()
            
            if len(filtered_timeline) > 0:
                # Convert dates
                filtered_timeline['Ngày bắt đầu'] = pd.to_datetime(filtered_timeline['Ngày bắt đầu'], errors='coerce')
                filtered_timeline['Ngày kết thúc'] = pd.to_datetime(filtered_timeline['Ngày kết thúc'], errors='coerce')
                
                # Filter by current month
                month_start = current_month.replace(day=1)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                # Get tasks that overlap with current month
                month_timeline = filtered_timeline[
                    (filtered_timeline['Ngày bắt đầu'] <= month_end) &
                    (filtered_timeline['Ngày kết thúc'] >= month_start)
                ].copy()
                
                # Generate calendar days
                days_in_month = (month_end - month_start).days + 1
                calendar_days = [month_start + timedelta(days=i) for i in range(days_in_month)]
                
                # Display tasks as clickable cards
                st.markdown("### 📋 Danh sách Task (Click để chỉnh sửa)")
                
                for idx, task in month_timeline.iterrows():
                    task_id = task['ID']
                    task_name = task['Giai đoạn']
                    task_status = task['Trạng thái']
                    task_progress = task['Tiến độ %']
                    task_person = task['Phụ trách']
                    task_priority = task.get('Độ ưu tiên', 'Trung bình')
                    task_start = task['Ngày bắt đầu']
                    task_end = task['Ngày kết thúc']
                    
                    # Status color
                    status_colors = {
                        'Chưa bắt đầu': '#ff6b6b',
                        'Đang thực hiện': '#51cf66',
                        'Hoàn thành': '#1f77b4',
                        'Trễ hạn': '#ff0000'
                    }
                    status_color = status_colors.get(task_status, '#999')
                    
                    # Priority emoji
                    priority_emoji = {'Cao': '🔴', 'Trung bình': '🟡', 'Thấp': '🟢'}.get(task_priority, '⚪')
                    
                    # Create expander for each task
                    with st.expander(f"{priority_emoji} **{task_name}** - {task_status} ({task_progress}%)", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**📅 Thời gian:** {task_start.strftime('%d/%m/%Y')} → {task_end.strftime('%d/%m/%Y')}")
                            st.markdown(f"**👤 Phụ trách:** {task_person}")
                            st.markdown(f"**📊 Tiến độ:** {task_progress}%")
                            st.markdown(f"**🎯 Độ ưu tiên:** {task_priority}")
                            if task.get('Mô tả'):
                                st.markdown(f"**📝 Mô tả:** {task['Mô tả']}")
                        
                        with col2:
                            # Quick update button
                            if st.button(f"✏️ Sửa", key=f"edit_{task_id}", use_container_width=True):
                                st.session_state[f'editing_task_{task_id}'] = True
                                st.rerun()
                        
                        # Edit form (show if editing)
                        if st.session_state.get(f'editing_task_{task_id}', False):
                            st.markdown("---")
                            st.markdown("### ✏️ Chỉnh sửa Task")
                            
                            with st.form(f"edit_form_{task_id}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    new_status = st.selectbox(
                                        "Trạng thái",
                                        ["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Trễ hạn"],
                                        index=["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Trễ hạn"].index(task_status)
                                    )
                                    new_progress = st.slider("Tiến độ (%)", 0, 100, int(task_progress))
                                
                                with col2:
                                    new_priority = st.selectbox(
                                        "Độ ưu tiên",
                                        ["Cao", "Trung bình", "Thấp"],
                                        index=["Cao", "Trung bình", "Thấp"].index(task_priority)
                                    )
                                    
                                    # Load danh sách nhân sự
                                    if len(members_df) > 0:
                                        member_names = members_df['Họ và tên'].tolist()
                                        current_person_idx = member_names.index(task_person) if task_person in member_names else 0
                                        new_person = st.selectbox("Phụ trách", member_names, index=current_person_idx)
                                    else:
                                        new_person = st.text_input("Phụ trách", value=task_person)
                                
                                new_note = st.text_area("Ghi chú cập nhật", placeholder="Thêm ghi chú về thay đổi...")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if st.form_submit_button("💾 Lưu thay đổi", use_container_width=True):
                                        # Update task in Google Sheets
                                        try:
                                            timeline_sheet = sheet.worksheet("Timeline")
                                            all_data = timeline_sheet.get_all_values()
                                            
                                            # Find row to update
                                            for row_idx, row in enumerate(all_data[1:], start=2):
                                                if row[0] == task_id:
                                                    # Update columns
                                                    timeline_sheet.update_cell(row_idx, 8, new_status)  # Trạng thái
                                                    timeline_sheet.update_cell(row_idx, 9, new_progress)  # Tiến độ
                                                    timeline_sheet.update_cell(row_idx, 10, new_priority)  # Độ ưu tiên
                                                    timeline_sheet.update_cell(row_idx, 7, new_person)  # Phụ trách
                                                    
                                                    # Add note to existing notes
                                                    current_note = row[10] if len(row) > 10 else ""
                                                    updated_note = f"{current_note}\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] {new_note}" if new_note else current_note
                                                    timeline_sheet.update_cell(row_idx, 11, updated_note)
                                                    
                                                    st.success("✅ Cập nhật thành công!")
                                                    st.session_state[f'editing_task_{task_id}'] = False
                                                    time.sleep(1)
                                                    st.rerun()
                                                    break
                                        except Exception as e:
                                            st.error(f"❌ Lỗi: {str(e)}")
                                
                                with col2:
                                    if st.form_submit_button("❌ Hủy", use_container_width=True):
                                        st.session_state[f'editing_task_{task_id}'] = False
                                        st.rerun()
                
                # Summary metrics
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📋 Tổng task", len(month_timeline))
                with col2:
                    completed = len(month_timeline[month_timeline['Trạng thái'] == 'Hoàn thành'])
                    st.metric("✅ Hoàn thành", completed)
                with col3:
                    in_progress = len(month_timeline[month_timeline['Trạng thái'] == 'Đang thực hiện'])
                    st.metric("▶️ Đang làm", in_progress)
                with col4:
                    avg_progress = month_timeline['Tiến độ %'].mean()
                    st.metric("📊 Tiến độ TB", f"{avg_progress:.0f}%")
                
            else:
                st.info("📭 Không có task nào trong tháng này.")
        else:
            st.warning("⚠️ Chưa có dự án nào. Vui lòng tạo dự án trước!")
    
    # TAB 2: Thêm giai đoạn (CẢI TIẾN - LOAD NHÂN SỰ)
    with tab2:
        if len(projects_df) > 0:
            st.subheader("➕ Thêm task/giai đoạn mới")
            
            with st.form("add_timeline_form"):
                project_id = st.selectbox(
                    "Chọn dự án *",
                    options=projects_df['ID'].tolist(),
                    format_func=lambda x: f"{x} - {projects_df[projects_df['ID']==x]['Tên dự án'].values[0]}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    giai_doan = st.text_input("Tên task *", placeholder="Ví dụ: Khảo sát địa điểm")
                    mo_ta = st.text_area("Mô tả", placeholder="Mô tả chi tiết công việc...")
                    ngay_bat_dau = st.date_input("Ngày bắt đầu *")
                    
                    # Load danh sách nhân sự từ Google Sheets
                    if len(members_df) > 0:
                        member_names = members_df['Họ và tên'].tolist()
                        phu_trach = st.selectbox("Phụ trách *", member_names)
                    else:
                        phu_trach = st.text_input("Phụ trách *", placeholder="Nguyễn Văn A")
                        st.info("💡 Chưa có nhân sự nào. Vui lòng thêm nhân sự ở trang Quản lý nhân sự!")
                
                with col2:
                    ngay_ket_thuc = st.date_input("Ngày kết thúc *")
                    trang_thai = st.selectbox("Trạng thái *", ["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Trễ hạn"])
                    tien_do = st.slider("Tiến độ (%)", 0, 100, 0)
                    do_uu_tien = st.selectbox("Độ ưu tiên", ["Cao", "Trung bình", "Thấp"])
                
                ghi_chu = st.text_input("Ghi chú", placeholder="Thông tin bổ sung...")
                
                submitted = st.form_submit_button("💾 Lưu task", use_container_width=True)
                
                if submitted:
                    if not giai_doan or not phu_trach:
                        st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                    elif ngay_ket_thuc < ngay_bat_dau:
                        st.error("❌ Ngày kết thúc phải sau ngày bắt đầu!")
                    else:
                        timeline_data = {
                            "ID": "",
                            "Project_ID": project_id,
                            "Giai đoạn": giai_doan,
                            "Mô tả": mo_ta,
                            "Ngày bắt đầu": ngay_bat_dau.strftime("%Y-%m-%d"),
                            "Ngày kết thúc": ngay_ket_thuc.strftime("%Y-%m-%d"),
                            "Phụ trách": phu_trach,
                            "Trạng thái": trang_thai,
                            "Tiến độ %": tien_do,
                            "Độ ưu tiên": do_uu_tien,
                            "Ghi chú": ghi_chu,
                            "Ngày tạo": ""
                        }
                        
                        if save_timeline(sheet, timeline_data):
                            st.success("✅ Đã thêm task thành công!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
        else:
            st.warning("⚠️ Chưa có dự án nào. Vui lòng tạo dự án trước!")

# ==================== PAGE 4: QUẢN LÝ KHÁCH HÀNG ====================
elif page == "👥 Quản lý Khách hàng":
    st.markdown('<div class="main-header">👥 QUẢN LÝ KHÁCH HÀNG</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "📊 Phân tích"])
    
    # TAB 1: Danh sách khách hàng
    with tab1:
        customers_df = load_customers(sheet)
        
        if len(customers_df) > 0:
            # Search
            search_term = st.text_input("🔍 Tìm kiếm:", placeholder="Tên, công ty, email...")
            
            if search_term:
                customers_df = customers_df[
                    customers_df['Tên khách hàng'].str.contains(search_term, case=False, na=False) |
                    customers_df['Công ty'].str.contains(search_term, case=False, na=False) |
                    customers_df['Email'].str.contains(search_term, case=False, na=False)
                ]
            
            st.markdown(f"**Tìm thấy {len(customers_df)} khách hàng**")
            
            # Display customers
            for idx, row in customers_df.iterrows():
                with st.expander(f"👤 {row['Tên khách hàng']} - {row['Công ty']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID:** {row['ID']}")
                        st.write(f"**Email:** {row['Email']}")
                        st.write(f"**Điện thoại:** {row['Điện thoại']}")
                    
                    with col2:
                        st.write(f"**Địa chỉ:** {row.get('Địa chỉ', 'N/A')}")
                        st.write(f"**Loại:** {row.get('Loại', 'N/A')}")
                        st.write(f"**Nguồn:** {row.get('Nguồn', 'N/A')}")
                    
                    with col3:
                        st.write(f"**Trạng thái:** {row['Trạng thái']}")
                        st.write(f"**Ngày tạo:** {row.get('Ngày tạo', 'N/A')}")
                    
                    st.write(f"**Ghi chú:** {row.get('Ghi chú', 'Không có')}")
                    
                    # Actions
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if st.button("🗑️ Xóa", key=f"delete_cus_{row['ID']}"):
                            if delete_customer(sheet, row['ID']):
                                st.success("Đã xóa khách hàng!")
                                st.rerun()
        else:
            st.info("📭 Chưa có khách hàng nào.")
    
    # TAB 2: Thêm khách hàng
    with tab2:
        st.subheader("➕ Thêm khách hàng mới")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                ten_kh = st.text_input("Tên khách hàng *", placeholder="Nguyễn Văn A")
                cong_ty = st.text_input("Công ty *", placeholder="ABC Corp")
                email = st.text_input("Email *", placeholder="example@company.com")
                dien_thoai = st.text_input("Điện thoại *", placeholder="0901234567")
            
            with col2:
                dia_chi = st.text_input("Địa chỉ", placeholder="123 Đường ABC, Quận 1, TP.HCM")
                loai = st.selectbox("Loại khách hàng", ["Cá nhân", "Doanh nghiệp", "Tổ chức", "Chính phủ"])
                nguon = st.selectbox("Nguồn", ["Website", "Giới thiệu", "Facebook", "Email", "Sự kiện", "Khác"])
                trang_thai = st.selectbox("Trạng thái", ["Tiềm năng", "Đang tư vấn", "Đã chốt", "Khách hàng thân thiết"])
            
            ghi_chu = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu khách hàng", use_container_width=True)
            
            if submitted:
                if not ten_kh or not cong_ty or not email:
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    customer_data = {
                        "ID": "",
                        "Tên khách hàng": ten_kh,
                        "Công ty": cong_ty,
                        "Email": email,
                        "Điện thoại": dien_thoai,
                        "Địa chỉ": dia_chi,
                        "Loại": loai,
                        "Nguồn": nguon,
                        "Trạng thái": trang_thai,
                        "Ghi chú": ghi_chu,
                        "Ngày tạo": ""
                    }
                    
                    if save_customer(sheet, customer_data):
                        st.success("✅ Đã thêm khách hàng thành công!")
                        st.balloons()
                        st.rerun()
    
    # TAB 3: Phân tích
    with tab3:
        customers_df = load_customers(sheet)
        
        if len(customers_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Khách hàng theo loại")
                type_dist = customers_df['Loại'].value_counts()
                fig = px.pie(values=type_dist.values, names=type_dist.index)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Khách hàng theo nguồn")
                source_dist = customers_df['Nguồn'].value_counts()
                fig = px.bar(x=source_dist.index, y=source_dist.values)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu để phân tích")

# ==================== PAGE 5: QUẢN LÝ NHÂN SỰ ====================
elif page == "👨‍💼 Quản lý Nhân sự":
    st.markdown('<div class="main-header">👨‍💼 QUẢN LÝ NHÂN SỰ</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "📊 Thống kê"])
    
    # TAB 1: Danh sách nhân sự
    with tab1:
        staff_df = load_staff(sheet)
        
        if len(staff_df) > 0:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                dept_filter = st.multiselect(
                    "Lọc theo phòng ban:",
                    options=staff_df['Phòng ban'].unique().tolist(),
                    default=staff_df['Phòng ban'].unique().tolist()
                )
            
            with col2:
                status_filter = st.multiselect(
                    "Lọc theo trạng thái:",
                    options=staff_df['Trạng thái'].unique().tolist(),
                    default=staff_df['Trạng thái'].unique().tolist()
                )
            
            with col3:
                search_term = st.text_input("🔍 Tìm kiếm:", placeholder="Tên, email...")
            
            # Apply filters
            filtered_df = staff_df[
                (staff_df['Phòng ban'].isin(dept_filter)) &
                (staff_df['Trạng thái'].isin(status_filter))
            ]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Họ tên'].str.contains(search_term, case=False, na=False) |
                    filtered_df['Email'].str.contains(search_term, case=False, na=False)
                ]
            
            st.markdown(f"**Tìm thấy {len(filtered_df)} nhân viên**")
            
            # Display staff cards
            cols = st.columns(3)
            for idx, row in filtered_df.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="staff-card">
                        <h3>👤 {row['Họ tên']}</h3>
                        <p><strong>Chức vụ:</strong> {row['Chức vụ']}</p>
                        <p><strong>Phòng ban:</strong> {row['Phòng ban']}</p>
                        <p><strong>Email:</strong> {row['Email']}</p>
                        <p><strong>Điện thoại:</strong> {row['Điện thoại']}</p>
                        <p><strong>Trạng thái:</strong> {row['Trạng thái']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️ Xóa", key=f"delete_staff_{row['ID']}"):
                        if delete_staff(sheet, row['ID']):
                            st.success("Đã xóa nhân viên!")
                            st.rerun()
        else:
            st.info("📭 Chưa có nhân viên nào.")
    
    # TAB 2: Thêm nhân viên
    with tab2:
        st.subheader("➕ Thêm nhân viên mới")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                ho_ten = st.text_input("Họ tên *", placeholder="Nguyễn Văn A")
                chuc_vu = st.text_input("Chức vụ *", placeholder="Event Manager")
                phong_ban = st.selectbox("Phòng ban *", ["Operations", "Sales", "Marketing", "Finance", "HR", "IT"])
                email = st.text_input("Email *", placeholder="nguyenvana@beevent.vn")
            
            with col2:
                dien_thoai = st.text_input("Điện thoại *", placeholder="0901234567")
                ngay_vao = st.date_input("Ngày vào làm *")
                luong = st.number_input("Lương (VNĐ)", min_value=0, step=1000000, format="%d")
                trang_thai = st.selectbox("Trạng thái *", ["Đang làm", "Nghỉ phép", "Đã nghỉ việc"])
            
            ky_nang = st.text_input("Kỹ năng", placeholder="Event Planning, Project Management...")
            ghi_chu = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu nhân viên", use_container_width=True)
            
            if submitted:
                if not ho_ten or not chuc_vu or not email:
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    staff_data = {
                        "ID": "",
                        "Họ tên": ho_ten,
                        "Chức vụ": chuc_vu,
                        "Phòng ban": phong_ban,
                        "Email": email,
                        "Điện thoại": dien_thoai,
                        "Ngày vào": ngay_vao.strftime("%Y-%m-%d"),
                        "Lương": luong,
                        "Trạng thái": trang_thai,
                        "Kỹ năng": ky_nang,
                        "Ghi chú": ghi_chu,
                        "Ngày tạo": ""
                    }
                    
                    if save_staff(sheet, staff_data):
                        st.success("✅ Đã thêm nhân viên thành công!")
                        st.balloons()
                        st.rerun()
    
    # TAB 3: Thống kê (tiếp tục)
    with tab3:
        staff_df = load_staff(sheet)
        
        if len(staff_df) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_staff = len(staff_df)
                active_staff = len(staff_df[staff_df['Trạng thái'] == 'Đang làm'])
                st.metric("👥 Tổng nhân sự", total_staff, f"{active_staff} đang làm")
            
            with col2:
                if 'Lương' in staff_df.columns:
                    avg_salary = pd.to_numeric(staff_df['Lương'], errors='coerce').mean()
                    st.metric("💰 Lương TB", f"{avg_salary/1_000_000:.1f}M VNĐ")
                else:
                    st.metric("💰 Lương TB", "N/A")
            
            with col3:
                dept_count = staff_df['Phòng ban'].nunique()
                st.metric("🏢 Số phòng ban", dept_count)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Nhân sự theo phòng ban")
                dept_dist = staff_df['Phòng ban'].value_counts()
                fig = px.bar(x=dept_dist.index, y=dept_dist.values)
                fig.update_layout(xaxis_title="Phòng ban", yaxis_title="Số người")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Nhân sự theo trạng thái")
                status_dist = staff_df['Trạng thái'].value_counts()
                fig = px.pie(values=status_dist.values, names=status_dist.index)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu để thống kê")

# ==================== PAGE 6: QUẢN LÝ TÀI CHÍNH ====================
elif page == "💰 Quản lý Tài chính":
    st.markdown('<div class="main-header">💰 QUẢN LÝ TÀI CHÍNH</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    finance_df = load_finance(sheet)
    
    tab1, tab2, tab3 = st.tabs(["📋 Giao dịch", "➕ Thêm giao dịch", "📊 Báo cáo tài chính"])
    
    # TAB 1: Danh sách giao dịch
    with tab1:
        if len(finance_df) > 0:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                type_filter = st.multiselect(
                    "Loại giao dịch:",
                    options=finance_df['Loại'].unique().tolist(),
                    default=finance_df['Loại'].unique().tolist()
                )
            
            with col2:
                status_filter = st.multiselect(
                    "Trạng thái:",
                    options=finance_df['Trạng thái'].unique().tolist(),
                    default=finance_df['Trạng thái'].unique().tolist()
                )
            
            with col3:
                if len(projects_df) > 0:
                    project_filter = st.selectbox(
                        "Dự án:",
                        options=['Tất cả'] + projects_df['ID'].tolist()
                    )
                else:
                    project_filter = 'Tất cả'
            
            # Apply filters
            filtered_df = finance_df[
                (finance_df['Loại'].isin(type_filter)) &
                (finance_df['Trạng thái'].isin(status_filter))
            ]
            
            if project_filter != 'Tất cả':
                filtered_df = filtered_df[filtered_df['Project_ID'] == project_filter]
            
            st.markdown(f"**Tìm thấy {len(filtered_df)} giao dịch**")
            
            # Display transactions
            for idx, row in filtered_df.iterrows():
                with st.expander(f"💵 {row['Hạng mục']} - {row['Loại']} - {pd.to_numeric(row['Số tiền'], errors='coerce'):,.0f} VNĐ"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID:** {row['ID']}")
                        st.write(f"**Dự án:** {row['Project_ID']}")
                        st.write(f"**Loại:** {row['Loại']}")
                    
                    with col2:
                        st.write(f"**Hạng mục:** {row['Hạng mục']}")
                        st.write(f"**Số tiền:** {pd.to_numeric(row['Số tiền'], errors='coerce'):,.0f} VNĐ")
                        st.write(f"**Ngày:** {row['Ngày']}")
                    
                    with col3:
                        st.write(f"**Người thanh toán:** {row['Người thanh toán']}")
                        st.write(f"**Trạng thái:** {row['Trạng thái']}")
                    
                    st.write(f"**Ghi chú:** {row.get('Ghi chú', 'Không có')}")
        else:
            st.info("📭 Chưa có giao dịch nào.")
    
    # TAB 2: Thêm giao dịch
    with tab2:
        if len(projects_df) > 0:
            st.subheader("➕ Thêm giao dịch mới")
            
            with st.form("add_finance_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    project_id = st.selectbox(
                        "Chọn dự án *",
                        options=projects_df['ID'].tolist(),
                        format_func=lambda x: f"{x} - {projects_df[projects_df['ID']==x]['Tên dự án'].values[0]}"
                    )
                    loai = st.selectbox("Loại giao dịch *", ["Thu", "Chi"])
                    hang_muc = st.text_input("Hạng mục *", placeholder="Ví dụ: Thanh toán venue")
                    so_tien = st.number_input("Số tiền (VNĐ) *", min_value=0, step=100000, format="%d")
                
                with col2:
                    ngay = st.date_input("Ngày giao dịch *")
                    nguoi_thanh_toan = st.text_input("Người thanh toán *", placeholder="Nguyễn Văn A")
                    trang_thai = st.selectbox("Trạng thái *", ["Chờ duyệt", "Đã duyệt", "Đã thanh toán", "Từ chối"])
                
                ghi_chu = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
                
                submitted = st.form_submit_button("💾 Lưu giao dịch", use_container_width=True)
                
                if submitted:
                    if not hang_muc or not nguoi_thanh_toan:
                        st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                    else:
                        finance_data = {
                            "ID": "",
                            "Project_ID": project_id,
                            "Loại": loai,
                            "Hạng mục": hang_muc,
                            "Số tiền": so_tien,
                            "Ngày": ngay.strftime("%Y-%m-%d"),
                            "Người thanh toán": nguoi_thanh_toan,
                            "Trạng thái": trang_thai,
                            "Ghi chú": ghi_chu,
                            "Ngày tạo": ""
                        }
                        
                        if save_finance(sheet, finance_data):
                            st.success("✅ Đã thêm giao dịch thành công!")
                            st.rerun()
        else:
            st.warning("⚠️ Chưa có dự án nào. Vui lòng tạo dự án trước!")
    
    # TAB 3: Báo cáo tài chính
    with tab3:
        if len(finance_df) > 0:
            # Convert to numeric
            finance_df['Số tiền'] = pd.to_numeric(finance_df['Số tiền'], errors='coerce')
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = finance_df[finance_df['Loại'] == 'Thu']['Số tiền'].sum()
                st.metric("💰 Tổng thu", f"{total_revenue/1_000_000:,.1f}M")
            
            with col2:
                total_expense = finance_df[finance_df['Loại'] == 'Chi']['Số tiền'].sum()
                st.metric("💸 Tổng chi", f"{total_expense/1_000_000:,.1f}M")
            
            with col3:
                net_profit = total_revenue - total_expense
                st.metric("📊 Lãi/Lỗ", f"{net_profit/1_000_000:,.1f}M", 
                         delta=f"{(net_profit/total_revenue*100):.1f}%" if total_revenue > 0 else "0%")
            
            with col4:
                pending = len(finance_df[finance_df['Trạng thái'] == 'Chờ duyệt'])
                st.metric("⏳ Chờ duyệt", pending)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Thu/Chi theo hạng mục")
                category_summary = finance_df.groupby(['Loại', 'Hạng mục'])['Số tiền'].sum().reset_index()
                fig = px.bar(category_summary, x='Hạng mục', y='Số tiền', color='Loại', barmode='group')
                fig.update_layout(yaxis_title="Số tiền (VNĐ)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🥧 Phân bổ chi phí")
                expense_data = finance_df[finance_df['Loại'] == 'Chi'].groupby('Hạng mục')['Số tiền'].sum()
                if len(expense_data) > 0:
                    fig = px.pie(values=expense_data.values, names=expense_data.index)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu chi phí")
            
            # Cash flow by project
            st.subheader("💵 Dòng tiền theo dự án")
            project_cashflow = finance_df.groupby(['Project_ID', 'Loại'])['Số tiền'].sum().unstack(fill_value=0)
            
            if 'Thu' in project_cashflow.columns and 'Chi' in project_cashflow.columns:
                project_cashflow['Lãi/Lỗ'] = project_cashflow['Thu'] - project_cashflow['Chi']
                st.dataframe(project_cashflow.style.format("{:,.0f}"), use_container_width=True)
            else:
                st.info("Chưa đủ dữ liệu để hiển thị dòng tiền")
        else:
            st.info("Chưa có dữ liệu tài chính để báo cáo")

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
                
                lost_from_lead = max(0, lead_count - qualified_count)
                lost_from_qualified = max(0, qualified_count - proposal_count)
                lost_from_proposal = max(0, proposal_count - won_count)
                
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

# ==================== PAGE 8: CÀI ĐẶT ====================
elif page == "⚙️ Cài đặt":
    st.markdown('<div class="main-header">⚙️ CÀI ĐẶT HỆ THỐNG</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔧 Cấu hình", "📤 Export/Import", "ℹ️ Thông tin"])
    
    with tab1:
        st.subheader("🔧 Cấu hình hệ thống")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Google Sheets**")
            st.info(f"✅ Đã kết nối: {sheet.title if sheet else 'Chưa kết nối'}")
            
            if st.button("🔄 Làm mới kết nối"):
                st.cache_resource.clear()
                st.success("Đã làm mới!")
                st.rerun()
        
        with col2:
            st.write("**Mục tiêu 2026**")
            target_revenue = st.number_input("Doanh thu (M VNĐ)", value=80000, step=1000)
            target_profit = st.number_input("Lãi gộp (M VNĐ)", value=13920, step=100)
            
            if st.button("💾 Lưu mục tiêu"):
                st.success("Đã lưu mục tiêu!")
    
    with tab2:
        st.subheader("📤 Export/Import dữ liệu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export dữ liệu**")
            
            export_type = st.selectbox("Chọn loại dữ liệu:", ["Dự án", "Khách hàng", "Nhân sự", "Tài chính"])
            
            if st.button("📥 Export to CSV"):
                if export_type == "Dự án":
                    df = load_projects(sheet)
                elif export_type == "Khách hàng":
                    df = load_customers(sheet)
                elif export_type == "Nhân sự":
                    df = load_staff(sheet)
                else:
                    df = load_finance(sheet)
                
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="⬇️ Tải xuống CSV",
                    data=csv,
                    file_name=f"{export_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.write("**Import dữ liệu**")
            st.info("💡 Tính năng đang phát triển...")
    
    with tab3:
        st.subheader("ℹ️ Thông tin hệ thống")
        
        st.markdown("""
        ### 🎯 Beevent Management System v2.0
        
        **Tính năng chính:**
        - ✅ Quản lý dự án (CRUD)
        - ✅ Timeline & Gantt Chart
        - ✅ Quản lý khách hàng
        - ✅ Quản lý nhân sự
        - ✅ Quản lý tài chính
        - ✅ Dashboard & Báo cáo (4 loại)
        - ✅ Kết nối Google Sheets
        - ✅ Export CSV
        
        **Công nghệ:**
        - Streamlit 1.40+
        - Google Sheets API
        - Plotly Charts
        - Pandas
        
        **Phát triển bởi:** Beevent Team
        
        **Liên hệ:** support@beevent.vn
        """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            projects_count = len(load_projects(sheet))
            st.metric("📋 Dự án", projects_count)
        
        with col2:
            customers_count = len(load_customers(sheet))
            st.metric("👥 Khách hàng", customers_count)
        
        with col3:
            staff_count = len(load_staff(sheet))
            st.metric("👨‍💼 Nhân sự", staff_count)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Beevent Management System v2.0</strong> | Powered by Streamlit & Google Sheets</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)

