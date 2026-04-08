import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام تدقيق مخيم الأزرق 2026", layout="wide")

# بيانات الدخول
USER_CREDENTIALS = {"Zaid": "1234"}

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
    SHAREPOINT_URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?download=1"

    @st.cache_data(ttl=600)
    def load_data():
        try:
            response = requests.get(SHAREPOINT_URL)
            # قراءة ملف الإكسل
            data = pd.read_excel(BytesIO(response.content))
            
            # تنظيف البيانات الأساسية وتحويل الأعمدة الرقمية لنصوص
            for col in data.columns:
                data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
            return data
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            return None

    df = load_data()

    if df is not None:
        # --- 3. الشريط الجانبي ---
        st.sidebar.title("🛠 خيارات التحكم")
        
        # تصحيح السطر الذي ظهر فيه الخطأ في الصورة
        if st.sidebar.button("تحديث البيانات"):
            st.cache_data.clear()
            st.rerun()
        
        if st.sidebar.button("تسجيل الخروج"):
            st.session_state["authenticated"] = False
            st.rerun()

        # --- 4. واجهة العرض الرئيسية ---
        st.title("📊 نظام إدارة وأرشفة سجلات المتطوعين - 2026")
        
        # إحصائيات علوية
        c1, c2 = st.columns(2)
        c1.metric("إجمالي السجلات", len(df))
        c2.metric("حالة القاعدة", "متصلة ✅")

        st.divider()

        # --- 5. محرك البحث ---
        st.subheader("🔍 محرك البحث الذكي")
        search_query = st.text_input("ادخل الاسم أو الرقم للبحث الفوري")

        # منطق الفلترة
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
        else:
            filtered_df = df

        # عرض النتائج
        st.dataframe(filtered_df, use_container_width=True)
        
        # زر التحميل
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل النتائج الحالية", data=csv, file_name="Azraq_HR_Data.csv", mime="text/csv")
