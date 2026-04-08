import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام تدقيق مخيم الأزرق 2026", layout="wide")

USER_CREDENTIALS = {"zaid": "1111"}

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

if check_password():
    # --- 2. جلب البيانات من SharePoint ---
    SHAREPOINT_URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?download=1"

    @st.cache_data(ttl=600)
    def load_data():
        try:
            response = requests.get(SHAREPOINT_URL)
            data = pd.read_excel(BytesIO(response.content))
            for col in data.columns:
                data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
            return data
        except Exception as e:
            st.error(f"❌ خطأ في الاتصال بقاعدة البيانات")
            return None

    df = load_data()

    if df is not None:
        # --- 3. الشريط الجانبي ---
        st.sidebar.title("🛠 خيارات التحكم")
        if st.sidebar.button("تحديث البيانات"):
            st.cache_data.clear()
            st.rerun()
        
        if st.sidebar.button("تسجيل الخروج"):
            st.session_state["authenticated"] = False
            st.rerun()

        # --- 4. واجهة العرض الرئيسية ---
        st.title("📊 نظام إدارة وأرشفة سجلات المتطوعين - 2026")
        
        c1, c2 = st.columns(2)
        c1.metric("إجمالي السجلات", len(df))
        c2.metric("حالة الوصول", "عرض فقط (محمي) 🔒")

        st.divider()

        # --- 5. محرك البحث الذكي ---
        st.subheader("🔍 محرك البحث")
        search_query = st.text_input("ابحث بواسطة الاسم، الرقم الفردي، أو رقم الهاتف")

        # سيتم عرض الجدول بدون أي خيارات تنزيل أو تصدير
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
            st.info(f"💡 تم العثور على {len(filtered_df)} نتيجة.")
            
            # عرض الجدول مع تعطيل شريط الأدوات (منع التنزيل)
            st.dataframe(filtered_df, use_container_width=True, column_config=None)
        else:
            st.write("أدخل بيانات البحث لعرض النتائج...")
            # عرض أول 10 سجلات كمعاينة بدون خيارات تنزيل
            st.dataframe(df.head(10), use_container_width=True)
            
        # إضافة تنسيق CSS لإخفاء زر التنزيل تماماً من واجهة المستخدم
        st.markdown(
            """
            <style>
            [data-testid="stElementToolbar"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    else:
        st.warning("⚠️ لا يمكن الوصول للقاعدة حالياً.")
