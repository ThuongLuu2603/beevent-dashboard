import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Beevent - Nhập liệu", page_icon="✍️", layout="wide")

st.title("✍️ BEEVENT - HỆ THỐNG NHẬP LIỆU")

SHEET_ID = "1xSvsEPHV1MzHa9UumzJtyzAY4LXaiSVKb8tmMcUZPeM"

# ==================== CONNECTION ====================
@st.cache_resource
def init_gsheet_connection():
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"❌ Lỗi kết nối: {str(e)}")
        return None

client = init_gsheet_connection()

if client:
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        st.sidebar.success("✅ Kết nối Google Sheets thành công!")
        
        # Chọn loại dữ liệu nhập
        data_type = st.sidebar.selectbox(
            "Chọn loại dữ liệu:",
            ["📊 Doanh thu tháng", "🎯 Sales Pipeline", "📋 Dự án", "👤 Sales Performance"]
        )
        
        st.markdown("---")
        
        # ==================== FORM 1: DOANH THU THÁNG ====================
        if data_type == "📊 Doanh thu tháng":
            st.header("📊 Nhập doanh thu theo tháng")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                with st.form("revenue_form"):
                    st.subheader("Thông tin doanh thu")
                    
                    month = st.date_input("Tháng:", datetime.now())
                    noi_bo = st.number_input("Nội bộ (VNĐ):", min_value=0, step=1000000, format="%d")
                    gov = st.number_input("Gov-Hiệp hội (VNĐ):", min_value=0, step=1000000, format="%d")
                    corporate = st.number_input("Corporate (VNĐ):", min_value=0, step=1000000, format="%d")
                    
                    submitted = st.form_submit_button("💾 Lưu dữ liệu", type="primary")
                    
                    if submitted:
                        try:
                            worksheet = spreadsheet.worksheet('revenue_monthly')
                            
                            new_row = [
                                month.strftime("%Y-%m-01"),
                                int(noi_bo),
                                int(gov),
                                int(corporate)
                            ]
                            
                            worksheet.append_row(new_row)
                            st.success("✅ Đã lưu dữ liệu thành công!")
                            st.balloons()
                            st.cache_data.clear()
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
            
            with col2:
                st.info(f"""
                **📊 Tổng cộng:**
                - Nội bộ: {noi_bo:,.0f} VNĐ
                - Gov: {gov:,.0f} VNĐ
                - Corporate: {corporate:,.0f} VNĐ
                
                **💰 Tổng: {(noi_bo + gov + corporate):,.0f} VNĐ**
                """)
            
            # Hiển thị dữ liệu hiện tại
            st.markdown("---")
            st.subheader("📋 Dữ liệu hiện tại")
            
            try:
                worksheet = spreadsheet.worksheet('revenue_monthly')
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                
                if len(df) > 0:
                    df['Tổng'] = df['Nội bộ'] + df['Gov-Hiệp hội'] + df['Corporate']
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    # Nút xóa dòng
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        row_to_delete = st.number_input("Xóa dòng số:", min_value=2, max_value=len(df)+1, step=1, key="delete_revenue")
                    with col2:
                        if st.button("🗑️ Xóa dòng"):
                            worksheet.delete_rows(row_to_delete)
                            st.success(f"✅ Đã xóa dòng {row_to_delete}")
                            st.cache_data.clear()
                            st.rerun()
                else:
                    st.info("Chưa có dữ liệu")
                    
            except Exception as e:
                st.error(f"❌ Lỗi load dữ liệu: {str(e)}")
        
        # ==================== FORM 2: SALES PIPELINE ====================
        elif data_type == "🎯 Sales Pipeline":
            st.header("🎯 Cập nhật Sales Pipeline")
            
            with st.form("pipeline_form"):
                st.subheader("Nhập số liệu từng giai đoạn")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    lead_count = st.number_input("Lead - Số lượng:", min_value=0, step=1, format="%d")
                    lead_value = st.number_input("Lead - Giá trị (M):", min_value=0, step=100, format="%d")
                    
                    qualified_count = st.number_input("Qualified - Số lượng:", min_value=0, step=1, format="%d")
                    qualified_value = st.number_input("Qualified - Giá trị (M):", min_value=0, step=100, format="%d")
                
                with col2:
                    proposal_count = st.number_input("Proposal - Số lượng:", min_value=0, step=1, format="%d")
                    proposal_value = st.number_input("Proposal - Giá trị (M):", min_value=0, step=100, format="%d")
                    
                    won_count = st.number_input("Won - Số lượng:", min_value=0, step=1, format="%d")
                    won_value = st.number_input("Won - Giá trị (M):", min_value=0, step=100, format="%d")
                
                submitted = st.form_submit_button("💾 Cập nhật Pipeline", type="primary")
                
                if submitted:
                    try:
                        worksheet = spreadsheet.worksheet('sales_pipeline')
                        
                        # Xóa dữ liệu cũ (giữ header)
                        worksheet.clear()
                        worksheet.append_row(['Stage', 'Count', 'Value'])
                        
                        # Thêm dữ liệu mới
                        worksheet.append_rows([
                            ['Lead', int(lead_count), int(lead_value)],
                            ['Qualified', int(qualified_count), int(qualified_value)],
                            ['Proposal', int(proposal_count), int(proposal_value)],
                            ['Won', int(won_count), int(won_value)]
                        ])
                        
                        st.success("✅ Đã cập nhật pipeline!")
                        st.balloons()
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"❌ Lỗi: {str(e)}")
            
            # Conversion rates
            if lead_count > 0:
                st.markdown("---")
                st.subheader("📊 Tỷ lệ chuyển đổi")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Lead → Qualified", f"{(qualified_count/lead_count*100):.1f}%")
                with col2:
                    st.metric("Qualified → Proposal", f"{(proposal_count/qualified_count*100):.1f}%" if qualified_count > 0 else "0%")
                with col3:
                    st.metric("Proposal → Won", f"{(won_count/proposal_count*100):.1f}%" if proposal_count > 0 else "0%")
        
        # ==================== FORM 3: DỰ ÁN ====================
        elif data_type == "📋 Dự án":
            st.header("📋 Nhập thông tin dự án")
            
            with st.form("project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    project_name = st.text_input("Tên dự án:", placeholder="Event ABC 2026")
                    revenue = st.number_input("Doanh thu (VNĐ):", min_value=0, step=1000000, format="%d")
                    profit_pct = st.number_input("Lợi nhuận (%):", min_value=0.0, max_value=100.0, step=0.1)
                
                with col2:
                    guests = st.number_input("Số khách:", min_value=0, step=10, format="%d")
                    event_type = st.selectbox("Loại sự kiện:", ["Teambuilding", "Gala", "Conference", "Festival", "Year End Party", "Khác"])
                    csat = st.slider("CSAT:", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
                
                submitted = st.form_submit_button("💾 Lưu dự án", type="primary")
                
                if submitted:
                    if project_name:
                        try:
                            worksheet = spreadsheet.worksheet('projects')
                            
                            new_row = [
                                project_name,
                                int(revenue),
                                float(profit_pct),
                                int(guests),
                                event_type,
                                float(csat)
                            ]
                            
                            worksheet.append_row(new_row)
                            st.success(f"✅ Đã lưu dự án: {project_name}")
                            st.balloons()
                            st.cache_data.clear()
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
                    else:
                        st.warning("⚠️ Vui lòng nhập tên dự án")
            
            # Hiển thị danh sách dự án
            st.markdown("---")
            st.subheader("📋 Danh sách dự án")
            
            try:
                worksheet = spreadsheet.worksheet('projects')
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                
                if len(df) > 0:
                    df_display = df.copy()
                    df_display['Doanh thu'] = df_display['Doanh thu'].apply(lambda x: f"{x/1_000_000:.1f}M")
                    st.dataframe(df_display, use_container_width=True, height=400)
                else:
                    st.info("Chưa có dự án nào")
                    
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
        
        # ==================== FORM 4: SALES PERFORMANCE ====================
        else:
            st.header("👤 Nhập hiệu suất Sales")
            
            with st.form("sales_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    sales_name = st.text_input("Tên nhân viên:", placeholder="Nguyễn Văn A")
                    revenue = st.number_input("Doanh thu (VNĐ):", min_value=0, step=1000000, format="%d")
                    deals = st.number_input("Số deal:", min_value=0, step=1, format="%d")
                
                with col2:
                    conversion = st.number_input("Conversion rate (%):", min_value=0.0, max_value=100.0, step=0.1)
                    channel = st.selectbox("Kênh:", ["Nội bộ", "Gov", "Corporate"])
                
                submitted = st.form_submit_button("💾 Lưu dữ liệu", type="primary")
                
                if submitted:
                    if sales_name:
                        try:
                            worksheet = spreadsheet.worksheet('sales_performance')
                            
                            new_row = [
                                sales_name,
                                int(revenue),
                                int(deals),
                                float(conversion),
                                channel
                            ]
                            
                            worksheet.append_row(new_row)
                            st.success(f"✅ Đã lưu dữ liệu cho: {sales_name}")
                            st.balloons()
                            st.cache_data.clear()
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi: {str(e)}")
                    else:
                        st.warning("⚠️ Vui lòng nhập tên nhân viên")
            
            # Leaderboard
            st.markdown("---")
            st.subheader("🏆 Bảng xếp hạng")
            
            try:
                worksheet = spreadsheet.worksheet('sales_performance')
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                
                if len(df) > 0:
                    df_sorted = df.sort_values('Doanh thu', ascending=False).reset_index(drop=True)
                    df_sorted['Rank'] = range(1, len(df_sorted) + 1)
                    df_display = df_sorted.copy()
                    df_display['Doanh thu'] = df_display['Doanh thu'].apply(lambda x: f"{x/1_000_000:.1f}M")
                    
                    st.dataframe(df_display[['Rank', 'Nhân viên', 'Doanh thu', 'Số deal', 'Conversion %', 'Kênh']], 
                               use_container_width=True, height=400)
                else:
                    st.info("Chưa có dữ liệu")
                    
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Không thể mở sheet: {str(e)}")
else:
    st.error("❌ Không thể kết nối Google Sheets. Kiểm tra secrets configuration.")
