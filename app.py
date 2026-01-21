import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

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
    .stButton>button:hover {
        background-color: #0d5a9e;
    }
    .timeline-item {
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
        margin-bottom: 1rem;
        position: relative;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -7px;
        top: 0;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #1f77b4;
    }
    .staff-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .gantt-bar {
        height: 30px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        padding-left: 10px;
        margin: 5px 0;
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

# ==================== SIDEBAR ====================
st.sidebar.title("🎯 BEEVENT SYSTEM")
st.sidebar.markdown("---")

# Kết nối Google Sheets
sheet = init_google_sheets()

if sheet is None:
    st.error("⚠️ Không thể kết nối Google Sheets. Vui lòng kiểm tra cấu hình!")
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
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách dự án", "➕ Tạo dự án mới", "📊 Phân tích"])
    
    with tab1:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Trạng thái:",
                    options=projects_df['Trạng thái'].unique() if 'Trạng thái' in projects_df.columns else [],
                    default=projects_df['Trạng thái'].unique() if 'Trạng thái' in projects_df.columns else []
                )
            
            with col2:
                type_filter = st.multiselect(
                    "Loại event:",
                    options=projects_df['Loại'].unique() if 'Loại' in projects_df.columns else [],
                    default=projects_df['Loại'].unique() if 'Loại' in projects_df.columns else []
                )
            
            with col3:
                search = st.text_input("🔍 Tìm kiếm:", placeholder="Tên dự án, khách hàng...")
            
            filtered_df = projects_df.copy()
            if status_filter and 'Trạng thái' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Trạng thái'].isin(status_filter)]
            if type_filter and 'Loại' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Loại'].isin(type_filter)]
            if search:
                filtered_df = filtered_df[
                    filtered_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
                ]
            
            st.markdown(f"**Tìm thấy {len(filtered_df)} dự án**")
            st.dataframe(filtered_df, hide_index=True, use_container_width=True, height=400)
            
            if st.button("📥 Xuất Excel"):
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "⬇️ Tải file",
                    csv,
                    f"projects_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        else:
            st.info("📋 Chưa có dự án nào. Hãy tạo dự án đầu tiên!")
    
    with tab2:
        st.subheader("➕ Thêm dự án mới")
        
        staff_df = load_staff(sheet)
        staff_list = staff_df['Họ tên'].tolist() if len(staff_df) > 0 else []
        
        with st.form("new_project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("Tên dự án *", placeholder="VD: Year End Party 2026")
                customer = st.text_input("Khách hàng *", placeholder="VD: Công ty ABC")
                event_type = st.selectbox("Loại event *", [
                    "Teambuilding", "Gala Dinner", "Year End Party", 
                    "Conference", "Festival", "Workshop", "Khác"
                ])
                start_date = st.date_input("Ngày bắt đầu *", value=datetime.now())
                end_date = st.date_input("Ngày kết thúc *", value=datetime.now() + timedelta(days=1))
            
            with col2:
                revenue = st.number_input("Doanh thu (VNĐ) *", min_value=0, step=1000000, format="%d")
                cost = st.number_input("Chi phí (VNĐ)", min_value=0, step=1000000, format="%d")
                pic = st.selectbox("PIC (Người phụ trách) *", [""] + staff_list)
                team = st.multiselect("Team thực hiện", staff_list)
                status = st.selectbox("Trạng thái", [
                    "Lead", "Đang đàm phán", "Đã ký HĐ", "Đang thực hiện", "Hoàn thành", "Hủy"
                ])
            
            notes = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu dự án", use_container_width=True)
            
            if submitted:
                if not project_name or not customer or not pic:
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    profit_pct = ((revenue - cost) / revenue * 100) if revenue > 0 else 0
                    
                    project_data = {
                        "ID": "",
                        "Tên dự án": project_name,
                        "Khách hàng": customer,
                        "Loại": event_type,
                        "Ngày bắt đầu": start_date.strftime("%Y-%m-%d"),
                        "Ngày kết thúc": end_date.strftime("%Y-%m-%d"),
                        "Doanh thu": revenue,
                        "Chi phí": cost,
                        "Lợi nhuận %": round(profit_pct, 2),
                        "Trạng thái": status,
                        "PIC": pic,
                        "Team": ", ".join(team),
                        "Ghi chú": notes,
                        "Ngày tạo": ""
                    }
                    
                    if save_project(sheet, project_data):
                        st.success("✅ Đã lưu dự án thành công!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Có lỗi xảy ra!")
    
    with tab3:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            st.subheader("📊 Phân tích dự án")
            
            projects_df['Doanh thu'] = pd.to_numeric(projects_df['Doanh thu'], errors='coerce')
            projects_df['Lợi nhuận %'] = pd.to_numeric(projects_df['Lợi nhuận %'], errors='coerce')
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Loại' in projects_df.columns:
                    revenue_by_type = projects_df.groupby('Loại')['Doanh thu'].sum().sort_values(ascending=False)
                    fig = px.bar(
                        x=revenue_by_type.values / 1_000_000,
                        y=revenue_by_type.index,
                        orientation='h',
                        title="Doanh thu theo loại event",
                        labels={'x': 'Doanh thu (M VNĐ)', 'y': 'Loại event'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Trạng thái' in projects_df.columns:
                    status_dist = projects_df['Trạng thái'].value_counts()
                    fig = px.pie(values=status_dist.values, names=status_dist.index, title="Phân bố trạng thái")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu")

# ==================== PAGE 3: TIMELINE DỰ ÁN ====================
elif page == "📅 Timeline Dự án":
    st.markdown('<div class="main-header">📅 TIMELINE DỰ ÁN</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Gantt Chart", "📋 Danh sách Timeline", "➕ Thêm Timeline"])
    
    with tab1:
        st.subheader("📊 Gantt Chart - Tổng quan tiến độ")
        
        projects_df = load_projects(sheet)
        timeline_df = load_timeline(sheet)
        
        if len(timeline_df) > 0:
            # Chọn dự án
            project_list = projects_df['Tên dự án'].tolist() if len(projects_df) > 0 else []
            selected_project = st.selectbox("Chọn dự án:", ["Tất cả"] + project_list)
            
            # Filter timeline
            if selected_project != "Tất cả":
                project_id = projects_df[projects_df['Tên dự án'] == selected_project]['ID'].values[0]
                filtered_timeline = timeline_df[timeline_df['Project_ID'] == project_id]
            else:
                filtered_timeline = timeline_df
            
            if len(filtered_timeline) > 0:
                # Convert dates
                filtered_timeline['Ngày bắt đầu'] = pd.to_datetime(filtered_timeline['Ngày bắt đầu'])
                filtered_timeline['Ngày kết thúc'] = pd.to_datetime(filtered_timeline['Ngày kết thúc'])
                
                # Create Gantt Chart
                fig = go.Figure()
                
                colors = {
                    'Hoàn thành': '#28a745',
                    'Đang thực hiện': '#ffc107',
                    'Chưa bắt đầu': '#6c757d',
                    'Trễ hạn': '#dc3545'
                }
                
                for idx, row in filtered_timeline.iterrows():
                    fig.add_trace(go.Bar(
                        name=row['Giai đoạn'],
                        x=[row['Ngày kết thúc'] - row['Ngày bắt đầu']],
                        y=[row['Giai đoạn']],
                        base=row['Ngày bắt đầu'],
                        orientation='h',
                        marker=dict(color=colors.get(row['Trạng thái'], '#6c757d')),
                        text=f"{row['Tiến độ %']}%",
                        textposition='inside',
                        hovertemplate=f"<b>{row['Giai đoạn']}</b><br>" +
                                    f"Bắt đầu: {row['Ngày bắt đầu'].strftime('%d/%m/%Y')}<br>" +
                                    f"Kết thúc: {row['Ngày kết thúc'].strftime('%d/%m/%Y')}<br>" +
                                    f"Phụ trách: {row['Phụ trách']}<br>" +
                                    f"Tiến độ: {row['Tiến độ %']}%<extra></extra>"
                    ))
                
                fig.update_layout(
                    title="Timeline Gantt Chart",
                    xaxis_title="Thời gian",
                    yaxis_title="Giai đoạn",
                    height=max(400, len(filtered_timeline) * 50),
                    showlegend=False,
                    hovermode='closest'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Progress summary
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    completed = len(filtered_timeline[filtered_timeline['Trạng thái'] == 'Hoàn thành'])
                    st.metric("✅ Hoàn thành", completed)
                
                with col2:
                    in_progress = len(filtered_timeline[filtered_timeline['Trạng thái'] == 'Đang thực hiện'])
                    st.metric("🔄 Đang thực hiện", in_progress)
                
                with col3:
                    not_started = len(filtered_timeline[filtered_timeline['Trạng thái'] == 'Chưa bắt đầu'])
                    st.metric("⏳ Chưa bắt đầu", not_started)
                
                with col4:
                    avg_progress = filtered_timeline['Tiến độ %'].astype(float).mean()
                    st.metric("📊 Tiến độ TB", f"{avg_progress:.1f}%")
            else:
                st.info("Không có timeline cho dự án này")
        else:
            st.info("📅 Chưa có timeline nào. Hãy thêm timeline ở tab bên cạnh!")
    
    with tab2:
        st.subheader("📋 Danh sách Timeline")
        
        timeline_df = load_timeline(sheet)
        
        if len(timeline_df) > 0:
            # Add project name
            projects_df = load_projects(sheet)
            if len(projects_df) > 0:
                timeline_df = timeline_df.merge(
                    projects_df[['ID', 'Tên dự án']], 
                    left_on='Project_ID', 
                    right_on='ID', 
                    how='left'
                )
            
            st.dataframe(timeline_df, hide_index=True, use_container_width=True, height=400)
        else:
            st.info("Chưa có timeline nào")
    
    with tab3:
        st.subheader("➕ Thêm Timeline mới")
        
        projects_df = load_projects(sheet)
        staff_df = load_staff(sheet)
        
        if len(projects_df) == 0:
            st.warning("⚠️ Vui lòng tạo dự án trước khi thêm timeline!")
        else:
            project_list = projects_df['Tên dự án'].tolist()
            staff_list = staff_df['Họ tên'].tolist() if len(staff_df) > 0 else []
            
            with st.form("new_timeline_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_project = st.selectbox("Chọn dự án *", project_list)
                    phase = st.text_input("Giai đoạn *", placeholder="VD: Lên kế hoạch")
                    description = st.text_area("Mô tả", placeholder="Chi tiết công việc...")
                    start_date = st.date_input("Ngày bắt đầu *", value=datetime.now())
                    end_date = st.date_input("Ngày kết thúc *", value=datetime.now() + timedelta(days=7))
                
                with col2:
                    assignee = st.selectbox("Phụ trách *", [""] + staff_list)
                    status = st.selectbox("Trạng thái", [
                        "Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Trễ hạn"
                    ])
                    progress = st.slider("Tiến độ (%)", 0, 100, 0, 5)
                    notes = st.text_area("Ghi chú", placeholder="Ghi chú thêm...")
                
                submitted = st.form_submit_button("💾 Lưu Timeline", use_container_width=True)
                
                if submitted:
                    if not phase or not assignee:
                        st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                    else:
                        project_id = projects_df[projects_df['Tên dự án'] == selected_project]['ID'].values[0]
                        
                        timeline_data = {
                            "ID": "",
                            "Project_ID": project_id,
                            "Giai đoạn": phase,
                            "Mô tả": description,
                            "Ngày bắt đầu": start_date.strftime("%Y-%m-%d"),
                            "Ngày kết thúc": end_date.strftime("%Y-%m-%d"),
                            "Phụ trách": assignee,
                            "Trạng thái": status,
                            "Tiến độ %": progress,
                            "Ghi chú": notes,
                            "Ngày tạo": ""
                        }
                        
                        if save_timeline(sheet, timeline_data):
                            st.success("✅ Đã lưu timeline thành công!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Có lỗi xảy ra!")

# ==================== PAGE 4: QUẢN LÝ KHÁCH HÀNG ====================
elif page == "👥 Quản lý Khách hàng":
    st.markdown('<div class="main-header">👥 QUẢN LÝ KHÁCH HÀNG</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Danh sách khách hàng", "➕ Thêm khách hàng"])
    
    with tab1:
        customers_df = load_customers(sheet)
        
        if len(customers_df) > 0:
            st.dataframe(customers_df, hide_index=True, use_container_width=True, height=500)
        else:
            st.info("Chưa có khách hàng nào")
    
    with tab2:
        with st.form("new_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("Tên khách hàng *")
                company = st.text_input("Công ty")
                email = st.text_input("Email *")
                phone = st.text_input("Điện thoại *")
            
            with col2:
                address = st.text_area("Địa chỉ")
                customer_type = st.selectbox("Loại khách hàng", ["Nội bộ", "Corporate", "Gov", "Cá nhân"])
                source = st.selectbox("Nguồn", ["Website", "Referral", "Facebook", "Email", "Khác"])
                status = st.selectbox("Trạng thái", ["Mới", "Đang chăm sóc", "Khách hàng", "Ngừng"])
            
            submitted = st.form_submit_button("💾 Lưu khách hàng", use_container_width=True)
            
            if submitted:
                if not customer_name or not email or not phone:
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc")
                else:
                    customer_data = {
                        "ID": "",
                        "Tên khách hàng": customer_name,
                        "Công ty": company,
                        "Email": email,
                        "Điện thoại": phone,
                        "Địa chỉ": address,
                        "Loại": customer_type,
                        "Nguồn": source,
                        "Trạng thái": status,
                        "Ngày tạo": ""
                    }
                    
                    if save_customer(sheet, customer_data):
                        st.success("✅ Đã lưu khách hàng!")
                        st.rerun()

# ==================== PAGE 5: QUẢN LÝ NHÂN SỰ ====================
elif page == "👨‍💼 Quản lý Nhân sự":
    st.markdown('<div class="main-header">👨‍💼 QUẢN LÝ NHÂN SỰ</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Danh sách", "➕ Thêm nhân sự", "📊 Phân tích", "🎯 Hiệu suất"])
    
    with tab1:
        st.subheader("📋 Danh sách nhân sự")
        
        staff_df = load_staff(sheet)
        
        if len(staff_df) > 0:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                dept_filter = st.multiselect(
                    "Phòng ban:",
                    options=staff_df['Phòng ban'].unique() if 'Phòng ban' in staff_df.columns else [],
                    default=staff_df['Phòng ban'].unique() if 'Phòng ban' in staff_df.columns else []
                )
            
            with col2:
                position_filter = st.multiselect(
                    "Chức vụ:",
                    options=staff_df['Chức vụ'].unique() if 'Chức vụ' in staff_df.columns else [],
                    default=staff_df['Chức vụ'].unique() if 'Chức vụ' in staff_df.columns else []
                )
            
            with col3:
                status_filter = st.multiselect(
                    "Trạng thái:",
                    options=staff_df['Trạng thái'].unique() if 'Trạng thái' in staff_df.columns else [],
                    default=staff_df['Trạng thái'].unique() if 'Trạng thái' in staff_df.columns else []
                )
            
            # Apply filters
            filtered_df = staff_df.copy()
            if dept_filter and 'Phòng ban' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Phòng ban'].isin(dept_filter)]
            if position_filter and 'Chức vụ' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Chức vụ'].isin(position_filter)]
            if status_filter and 'Trạng thái' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Trạng thái'].isin(status_filter)]
            
            st.markdown(f"**Tìm thấy {len(filtered_df)} nhân sự**")
            st.dataframe(filtered_df, hide_index=True, use_container_width=True, height=400)
            
            if st.button("📥 Xuất Excel"):
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "⬇️ Tải file",
                    csv,
                    f"staff_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        else:
            st.info("👨‍💼 Chưa có nhân sự nào. Hãy thêm nhân sự ở tab bên cạnh!")
    
    with tab2:
        st.subheader("➕ Thêm nhân sự mới")
        
        with st.form("new_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Họ tên *", placeholder="VD: Nguyễn Văn A")
                position = st.selectbox("Chức vụ *", [
                    "Giám đốc", "Phó giám đốc", "Trưởng phòng", "Phó phòng",
                    "Nhân viên", "Thực tập sinh"
                ])
                department = st.selectbox("Phòng ban *", [
                    "Ban Giám đốc", "Kinh doanh", "Vận hành", "Marketing", 
                    "Kế toán", "Nhân sự", "IT"
                ])
                email = st.text_input("Email *", placeholder="example@beevent.vn")
                phone = st.text_input("Điện thoại *", placeholder="0912345678")
            
            with col2:
                join_date = st.date_input("Ngày vào làm *", value=datetime.now())
                salary = st.number_input("Lương (VNĐ)", min_value=0, step=1000000, format="%d")
                status = st.selectbox("Trạng thái", ["Đang làm", "Nghỉ việc", "Tạm nghỉ"])
                skills = st.text_area("Kỹ năng", placeholder="VD: Event Planning, Project Management, Communication")
                notes = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu nhân sự", use_container_width=True)
            
            if submitted:
                if not full_name or not email or not phone:
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    staff_data = {
                        "ID": "",
                        "Họ tên": full_name,
                        "Chức vụ": position,
                        "Phòng ban": department,
                        "Email": email,
                        "Điện thoại": phone,
                        "Ngày vào": join_date.strftime("%Y-%m-%d"),
                        "Lương": salary,
                        "Trạng thái": status,
                        "Kỹ năng": skills,
                        "Ghi chú": notes,
                        "Ngày tạo": ""
                    }
                    
                    if save_staff(sheet, staff_data):
                        st.success("✅ Đã lưu nhân sự thành công!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Có lỗi xảy ra!")
    
    with tab3:
        st.subheader("📊 Phân tích nhân sự")
        
        staff_df = load_staff(sheet)
        
        if len(staff_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Department distribution
                if 'Phòng ban' in staff_df.columns:
                    dept_dist = staff_df['Phòng ban'].value_counts()
                    fig = px.bar(
                        x=dept_dist.values,
                        y=dept_dist.index,
                        orientation='h',
                        title="Phân bố theo phòng ban",
                        labels={'x': 'Số lượng', 'y': 'Phòng ban'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Position distribution
                if 'Chức vụ' in staff_df.columns:
                    pos_dist = staff_df['Chức vụ'].value_counts()
                    fig = px.pie(
                        values=pos_dist.values,
                        names=pos_dist.index,
                        title="Phân bố theo chức vụ",
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Salary analysis
            if 'Lương' in staff_df.columns and 'Phòng ban' in staff_df.columns:
                st.subheader("💰 Phân tích lương theo phòng ban")
                staff_df['Lương'] = pd.to_numeric(staff_df['Lương'], errors='coerce')
                salary_by_dept = staff_df.groupby('Phòng ban')['Lương'].mean().sort_values(ascending=False)
                
                fig = px.bar(
                    x=salary_by_dept.values / 1_000_000,
                    y=salary_by_dept.index,
                    orientation='h',
                    title="Lương trung bình theo phòng ban",
                    labels={'x': 'Lương TB (Triệu VNĐ)', 'y': 'Phòng ban'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu để phân tích")
    
    with tab4:
        st.subheader("🎯 Hiệu suất làm việc")
        
        staff_df = load_staff(sheet)
        projects_df = load_projects(sheet)
        
        if len(staff_df) > 0 and len(projects_df) > 0:
            # Count projects per staff
            pic_counts = projects_df['PIC'].value_counts()
            
            # Create performance dataframe
            performance_df = pd.DataFrame({
                'Nhân viên': pic_counts.index,
                'Số dự án': pic_counts.values
            })
            
            # Merge with staff info
            performance_df = performance_df.merge(
                staff_df[['Họ tên', 'Phòng ban', 'Chức vụ']],
                left_on='Nhân viên',
                right_on='Họ tên',
                how='left'
            )
            
            # Display top performers
            st.markdown("### 🏆 Top Performers")
            
            col1, col2, col3 = st.columns(3)
            
            top_3 = performance_df.nlargest(3, 'Số dự án')
            
            for idx, (col, row) in enumerate(zip([col1, col2, col3], top_3.iterrows())):
                with col:
                    medal = ["🥇", "🥈", "🥉"][idx]
                    st.markdown(f"""
                    <div class="staff-card">
                        <h2 style="text-align: center;">{medal}</h2>
                        <h3 style="text-align: center;">{row[1]['Nhân viên']}</h3>
                        <p style="text-align: center; font-size: 1.2rem;">
                            <strong>{row[1]['Số dự án']}</strong> dự án
                        </p>
                        <p style="text-align: center;">{row[1]['Phòng ban']} - {row[1]['Chức vụ']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Full performance table
            st.markdown("### 📊 Bảng hiệu suất đầy đủ")
            st.dataframe(
                performance_df.sort_values('Số dự án', ascending=False),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Chưa có đủ dữ liệu để đánh giá hiệu suất")

# ==================== PAGE 6: TÀI CHÍNH ====================
elif page == "💰 Quản lý Tài chính":
    st.markdown('<div class="main-header">💰 QUẢN LÝ TÀI CHÍNH</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    
    if len(projects_df) > 0:
        projects_df['Doanh thu'] = pd.to_numeric(projects_df['Doanh thu'], errors='coerce')
        projects_df['Chi phí'] = pd.to_numeric(projects_df['Chi phí'], errors='coerce')
        projects_df['Lợi nhuận'] = projects_df['Doanh thu'] - projects_df['Chi phí']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_revenue = projects_df['Doanh thu'].sum() / 1_000_000
            st.metric("💰 Tổng doanh thu", f"{total_revenue:.1f}M")
        
        with col2:
            total_cost = projects_df['Chi phí'].sum() / 1_000_000
            st.metric("💸 Tổng chi phí", f"{total_cost:.1f}M")
        
        with col3:
            total_profit = projects_df['Lợi nhuận'].sum() / 1_000_000
            st.metric("📈 Lợi nhuận", f"{total_profit:.1f}M")
        
        st.markdown("---")
        
        st.subheader("📊 Chi tiết tài chính theo dự án")
        financial_df = projects_df[['Tên dự án', 'Doanh thu', 'Chi phí', 'Lợi nhuận', 'Lợi nhuận %', 'Trạng thái']]
        st.dataframe(financial_df, hide_index=True, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu tài chính")

# ==================== PAGE 7: DASHBOARD ====================
elif page == "📊 Dashboard & Báo cáo":
    st.markdown('<div class="main-header">📊 DASHBOARD & BÁO CÁO</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    
    if len(projects_df) > 0:
        st.info("📊 Dashboard tổng hợp (có thể tích hợp code dashboard cũ)")
    else:
        st.warning("⚠️ Chưa có dữ liệu để hiển thị dashboard")

# ==================== PAGE 8: CÀI ĐẶT ====================
else:
    st.markdown('<div class="main-header">⚙️ CÀI ĐẶT HỆ THỐNG</div>', unsafe_allow_html=True)
    
    st.subheader("🔗 Kết nối Google Sheets")
    
    if sheet:
        st.success(f"✅ Đã kết nối: **{sheet.title}**")
        st.info(f"📊 URL: {sheet.url}")
        
        if st.button("🔄 Làm mới kết nối"):
            st.cache_resource.clear()
            st.rerun()
    else:
        st.error("❌ Chưa kết nối Google Sheets")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Beevent Management System v2.0</strong> | Powered by Streamlit & Google Sheets</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
