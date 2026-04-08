import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

# --- 1. إعدادات الصفحة والأمان ---
st.set_page_config(page_title="نظام HR مخيم الأزرق 2026", layout="wide")

# CSS لإخفاء أدوات الجدول وتحسين المظهر
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] { display: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

USER_CREDENTIALS = {"zaid": "11111"}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.title("🔐 تسجيل الدخول")
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
            # تحويل كافة البيانات لنصوص لضمان دقة البحث
            for col in data.columns:
                data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
            return data
        except:
            return None

    df = load_data()

    if df is not None:
        tab1, tab2, tab3 = st.tabs(["🔍 البحث والتدقيق", "📊 لوحة الإحصائيات", "🛡️ أمن النظام"])

        with tab1:
            st.header("🔍 محرك البحث الذكي")
            search_query = st.text_input("ابحث بواسطة (الاسم، الرقم الفردي، أو رقم الهاتف)")
            
            if search_query:
                filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
                st.info(f"💡 تم العثور على {len(filtered_df)} نتيجة.")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df.head(10), use_container_width=True)

        with tab2:
            st.header("📊 تحليل بيانات المتطوعين")
            
            col_a, col_b = st.columns(2)
            
            # --- إصلاح رسم بياني للجنس (حل مشكلة الصورة الأخيرة) ---
            with col_a:
                if 'EmpGender' in df.columns:
                    st.subheader("👫 توزيع الجنس")
                    # معالجة البيانات بشكل آمن لتجنب أخطاء التسمية
                    gender_data = df['EmpGender'].value_counts().reset_index()
                    gender_data.columns = ['Gender', 'Count'] # إعادة تسمية الأعمدة يدوياً لضمان استقرار الكود
                    
                    fig_gen = px.bar(gender_data, x='Gender', y='Count', 
                                    color='Gender', text_auto=True,
                                    color_discrete_map={'Male': '#1f77b4', 'Female': '#e377c2'})
                    st.plotly_chart(fig_gen, use_container_width=True)
            
            with col_b:
                if 'Project' in df.columns:
                    st.subheader("📂 توزيع المشاريع")
                    fig_proj = px.pie(df, names='Project', hole=0.5, 
                                     color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig_proj, use_container_width=True)

            st.divider()
            
            # ميزة جديدة: توزيع المهارات
            if 'Skill Level' in df.columns:
                st.subheader("🛠️ مستويات المهارة للمتطوعين")
                skill_data = df['Skill Level'].value_counts().reset_index()
                skill_data.columns = ['Skill', 'Total']
                fig_skill = px.funnel(skill_data, x='Total', y='Skill', color='Skill')
                st.plotly_chart(fig_skill, use_container_width=True)

        with tab3:
            st.header("🛡️ حالة النظام")
            st.success("✅ النظام متصل بقاعدة بيانات SharePoint")
            st.info(f"📅 آخر تحديث للبيانات: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
            
            if st.button("🚪 تسجيل الخروج"):
                st.session_state["authenticated"] = False
                st.rerun()

        st.sidebar.title("⚙️ الإعدادات")
        if st.sidebar.button("🔄 تحديث يدوي"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("⚠️ فشل الاتصال بالقاعدة. تأكد من إعدادات المشاركة في SharePoint.")
