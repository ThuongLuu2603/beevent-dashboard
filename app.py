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
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GOOGLE SHEETS CONNECTION ====================
@st.cache_resource
def init_google_sheets():
    """Kết nối Google Sheets"""
    try:
        # Lấy credentials từ Streamlit secrets
        creds_dict = st.secrets["gcp_service_account"]
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Mở Google Sheet (tạo nếu chưa có)
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
def load_projects(sheet):
    """Load dữ liệu dự án từ Google Sheets"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Ghi chú", "Ngày tạo"
    ])
    
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=ws.row_values(1))
    return pd.DataFrame(data)

def save_project(sheet, project_data):
    """Lưu dự án mới"""
    ws = get_worksheet(sheet, "Projects", [
        "ID", "Tên dự án", "Khách hàng", "Loại", "Ngày bắt đầu", "Ngày kết thúc",
        "Doanh thu", "Chi phí", "Lợi nhuận %", "Trạng thái", "PIC", "Ghi chú", "Ngày tạo"
    ])
    
    # Tạo ID tự động
    existing_data = ws.get_all_records()
    new_id = len(existing_data) + 1
    
    project_data["ID"] = f"PRJ{new_id:04d}"
    project_data["Ngày tạo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ws.append_row(list(project_data.values()))
    return True

def update_project(sheet, project_id, updated_data):
    """Cập nhật dự án"""
    ws = sheet.worksheet("Projects")
    cell = ws.find(project_id)
    
    if cell:
        row_num = cell.row
        ws.update(f"A{row_num}:M{row_num}", [list(updated_data.values())])
        return True
    return False

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
        "👥 Quản lý Khách hàng",
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
    
    # Load data
    projects_df = load_projects(sheet)
    customers_df = load_customers(sheet)
    
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
        if len(projects_df) > 0 and 'Doanh thu' in projects_df.columns:
            total_revenue = pd.to_numeric(projects_df['Doanh thu'], errors='coerce').sum() / 1_000_000
            st.metric("💰 Doanh thu", f"{total_revenue:.1f}M", "+12%")
        else:
            st.metric("💰 Doanh thu", "0M", "Chưa có dữ liệu")
    
    with col4:
        if len(projects_df) > 0 and 'Lợi nhuận %' in projects_df.columns:
            avg_profit = pd.to_numeric(projects_df['Lợi nhuận %'], errors='coerce').mean()
            st.metric("📊 Biên LN TB", f"{avg_profit:.1f}%", "+2.3%")
        else:
            st.metric("📊 Biên LN TB", "0%", "Chưa có dữ liệu")
    
    st.markdown("---")
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dự án gần đây")
        if len(projects_df) > 0:
            recent_projects = projects_df.tail(5)[['Tên dự án', 'Khách hàng', 'Trạng thái', 'Ngày bắt đầu']]
            st.dataframe(recent_projects, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có dự án nào. Hãy tạo dự án đầu tiên!")
    
    with col2:
        st.subheader("👥 Khách hàng mới")
        if len(customers_df) > 0:
            recent_customers = customers_df.tail(5)[['Tên khách hàng', 'Công ty', 'Loại', 'Trạng thái']]
            st.dataframe(recent_customers, hide_index=True, use_container_width=True)
        else:
            st.info("Chưa có khách hàng nào. Hãy thêm khách hàng!")

# ==================== PAGE 2: QUẢN LÝ DỰ ÁN ====================
elif page == "📝 Quản lý Dự án":
    st.markdown('<div class="main-header">📝 QUẢN LÝ DỰ ÁN</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Danh sách dự án", "➕ Tạo dự án mới", "📊 Phân tích"])
    
    # TAB 1: Danh sách dự án
    with tab1:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            # Filters
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
            
            # Apply filters
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
            
            # Display table
            st.dataframe(
                filtered_df,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            # Export
            if st.button("📥 Xuất Excel"):
                csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "⬇️ Tải file",
                    csv,
                    f"projects_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        else:
            st.info("📋 Chưa có dự án nào. Hãy tạo dự án đầu tiên ở tab 'Tạo dự án mới'!")
    
    # TAB 2: Tạo dự án mới
    with tab2:
        st.subheader("➕ Thêm dự án mới")
        
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
            
            with col2:
                end_date = st.date_input("Ngày kết thúc *", value=datetime.now() + timedelta(days=1))
                revenue = st.number_input("Doanh thu (VNĐ) *", min_value=0, step=1000000, format="%d")
                cost = st.number_input("Chi phí (VNĐ)", min_value=0, step=1000000, format="%d")
                pic = st.text_input("PIC (Người phụ trách)", placeholder="VD: Nguyễn Văn A")
            
            status = st.selectbox("Trạng thái", [
                "Lead", "Đang đàm phán", "Đã ký HĐ", "Đang thực hiện", "Hoàn thành", "Hủy"
            ])
            
            notes = st.text_area("Ghi chú", placeholder="Thông tin bổ sung...")
            
            submitted = st.form_submit_button("💾 Lưu dự án", use_container_width=True)
            
            if submitted:
                if not project_name or not customer:
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc (*)")
                else:
                    profit_pct = ((revenue - cost) / revenue * 100) if revenue > 0 else 0
                    
                    project_data = {
                        "ID": "",  # Sẽ tự động tạo
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
                        "Ghi chú": notes,
                        "Ngày tạo": ""  # Sẽ tự động tạo
                    }
                    
                    if save_project(sheet, project_data):
                        st.success("✅ Đã lưu dự án thành công!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Có lỗi xảy ra. Vui lòng thử lại!")
    
    # TAB 3: Phân tích
    with tab3:
        projects_df = load_projects(sheet)
        
        if len(projects_df) > 0:
            st.subheader("📊 Phân tích dự án")
            
            # Convert to numeric
            projects_df['Doanh thu'] = pd.to_numeric(projects_df['Doanh thu'], errors='coerce')
            projects_df['Lợi nhuận %'] = pd.to_numeric(projects_df['Lợi nhuận %'], errors='coerce')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Revenue by type
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
                # Status distribution
                if 'Trạng thái' in projects_df.columns:
                    status_dist = projects_df['Trạng thái'].value_counts()
                    
                    fig = px.pie(
                        values=status_dist.values,
                        names=status_dist.index,
                        title="Phân bố trạng thái dự án"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu để phân tích")

# ==================== PAGE 3: QUẢN LÝ KHÁCH HÀNG ====================
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

# ==================== PAGE 4: TÀI CHÍNH ====================
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
        
        # Financial table
        st.subheader("📊 Chi tiết tài chính theo dự án")
        financial_df = projects_df[['Tên dự án', 'Doanh thu', 'Chi phí', 'Lợi nhuận', 'Lợi nhuận %', 'Trạng thái']]
        st.dataframe(financial_df, hide_index=True, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu tài chính")

# ==================== PAGE 5: DASHBOARD ====================
elif page == "📊 Dashboard & Báo cáo":
    st.markdown('<div class="main-header">📊 DASHBOARD & BÁO CÁO</div>', unsafe_allow_html=True)
    
    projects_df = load_projects(sheet)
    
    if len(projects_df) > 0:
        # Tái sử dụng code dashboard cũ ở đây
        st.info("📊 Dashboard tổng hợp (tích hợp code dashboard cũ)")
    else:
        st.warning("⚠️ Chưa có dữ liệu để hiển thị dashboard")

# ==================== PAGE 6: CÀI ĐẶT ====================
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
    <p><strong>Beevent Management System</strong> | Powered by Streamlit & Google Sheets</p>
    <p style='font-size: 0.8rem;'>Last updated: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
</div>
""", unsafe_allow_html=True)
