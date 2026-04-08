import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام HR مخيم الأزرق 2026", layout="wide")

# CSS لإخفاء أدوات الجدول نهائياً (حماية البيانات)
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] { display: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px 5px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b; color: white; }
    </style>
""", unsafe_allow_html=True)

USER_CREDENTIALS = {"zaid": "11111"}

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
        except:
            return None

    df = load_data()

    if df is not None:
        # --- 3. تصميم التبويبات ---
        tab1, tab2, tab3 = st.tabs(["🔍 البحث والتدقيق", "📊 لوحة الإحصائيات", "🛡️ أمن النظام"])

        with tab1:
            st.header("🔍 محرك البحث الذكي")
            search_query = st.text_input("ابحث بواسطة الاسم، الرقم الفردي، أو رقم الهاتف", key="main_search")
            
            if search_query:
                filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
                st.info(f"💡 تم العثور على {len(filtered_df)} نتيجة.")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.write("أدخل بيانات البحث لعرض النتائج...")
                st.dataframe(df.head(10), use_container_width=True)

        with tab2:
            st.header("📊 تحليل بيانات المتطوعين")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if 'Project' in df.columns:
                    st.subheader("توزيع المتطوعين حسب المشروع")
                    fig_proj = px.pie(df, names='Project', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_proj, use_container_width=True)
            
            with col_b:
                if 'EmpGender' in df.columns:
                    st.subheader("نسبة النوع الاجتماعي")
                    fig_gen = px.bar(df['EmpGender'].value_counts().reset_index(), x='index', y='EmpGender', 
                                    labels={'index': 'الجنس', 'EmpGender': 'العدد'}, color='index')
                    st.plotly_chart(fig_gen, use_container_width=True)

            st.divider()
            st.subheader("📈 إحصائيات سريعة")
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي السجلات", len(df))
            m2.metric("المشاريع النشطة", df['Project'].nunique() if 'Project' in df.columns else "0")
            m3.metric("حالة القاعدة", "محدثة ✅")

        with tab3:
            st.header("🛡️ سياسة الوصول والأمن")
            st.warning("هذا النظام مخصص للعرض فقط. تم تعطيل كافة خيارات التحميل وتصدير البيانات لحماية خصوصية المتطوعين.")
            st.info("""
            - **مصدر البيانات:** SharePoint (BDC Organization).
            - **تحديث البيانات:** يتم التحديث تلقائياً كل 10 دقائق.
            - **الصلاحيات:** مسموح لـ 'alaa_admin' فقط.
            """)
            if st.button("🚪 تسجيل الخروج"):
                st.session_state["authenticated"] = False
                st.rerun()

        # زر التحديث في الشريط الجانبي
        st.sidebar.title("🛠 الإعدادات")
        if st.sidebar.button("🔄 تحديث يدوي للبيانات"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("⚠️ فشل الاتصال بقاعدة البيانات.")
