import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام تدقيق مخيم الأزرق 2026", layout="wide")

USER_CREDENTIALS = {"alaa_admin": "azraq2026"} # يمكنك إضافة مستخدمين آخرين هنا

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.title("🔐 تسجيل الدخول - نظام HR")
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pw:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ البيانات غير صحيحة")
        return False
    return True

# --- تنفيذ البرنامج بعد تسجيل الدخول ---
if check_password():
    # --- 2. الاتصال بقاعدة البيانات المثبتة ---
    # ملاحظة: استبدل الرابط أدناه برابط ملف Google Sheets الخاص بك
    SHEET_URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?e=1jEGFr"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SHEET_URL)
        
        # تنظيف البيانات تلقائياً (تحويل الأرقام لنصوص لمنع ظهور الفواصل)
        id_cols = ['Individual Number', 'الرقم الأمني', 'EmpNo', 'رقم الهاتف']
        for col in id_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.0', '', regex=False).str.strip()
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        st.stop()

    # --- 3. الشريط الجانبي (إضافة بيانات وتحديث) ---
    st.sidebar.title("🛠 خيارات التحكم")
    
    if st.sidebar.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("➕ إضافة متطوع جديد")
    with st.sidebar.form("add_form"):
        new_name = st.text_input("الاسم الكامل")
        new_id = st.text_input("الرقم الفردي")
        new_status = st.selectbox("الحالة", ["Active", "Resigned", "Standby"])
        submit_button = st.form_submit_button("حفظ في القاعدة")
        
        if submit_button:
            # هنا يمكنك إضافة كود الحفظ (Write) لاحقاً عند تفعيل صلاحيات الكتابة
            st.sidebar.info("تم إرسال الطلب (تحتاج لربط صلاحيات الكتابة في Google Console)")

    # --- 4. واجهة العرض الرئيسية ---
    st.title("📊 نظام إدارة وأرشفة سجلات المتطوعين - 2026")
    
    # صناديق الإحصائيات السريعة (مثل مثال GDP الذي أعجبك)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المتطوعين", len(df))
    if 'Status' in df.columns:
        active_count = len(df[df['Status'] == 'Active'])
        col2.metric("الحالات النشطة", active_count)
        col3.metric("نسبة الإنجاز", f"{(active_count/len(df)*100):.1f}%")

    st.divider()

    # --- 5. نظام البحث الرباعي ---
    st.subheader("🔍 محرك البحث السريع")
    s1, s2, s3, s4 = st.columns(4)
    with s1: search_id = st.text_input("الرقم الفردي/الأمني")
    with s2: search_name = st.text_input("اسم المتطوع")
    with s3: search_phone = st.text_input("رقم الهاتف")
    with s4: filter_status = st.selectbox("تصفية حسب الحالة", ["الكل"] + list
