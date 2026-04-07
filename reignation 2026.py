import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام تدقيق مخيم الأزرق 2026", layout="wide")

# بيانات الدخول
USER_CREDENTIALS = {"alaa_admin": "azraq2026"}

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
    
    # --- 2. جلب البيانات من SharePoint ---
    # قمت بتعديل الرابط ليصبح رابط تحميل مباشر
    SHAREPOINT_URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?download=1"

    @st.cache_data(ttl=600) # تحديث تلقائي كل 10 دقائق
    def load_data():
        try:
            response = requests.get(SHAREPOINT_URL)
            # قراءة ملف الإكسل من الذاكرة
            data = pd.read_excel(BytesIO(response.content))
            
            # تنظيف البيانات الأساسية
            for col in data.columns:
                if "Number" in col or "رقم" in col or "ID" in col:
                    data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
            return data
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return None

    df = load_data()

    if df is not None:
        # --- 3. واجهة التحكم الجانبية ---
        st.sidebar.title("🛠 خيارات التحكم")
        if st.sidebar.button("🔄 تحديث
