import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import base64

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="نظام HR مخيم الأزرق 2026", layout="wide", page_icon="📝")

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# تحسين الخلفية ووضوح النصوص (إضافة طبقة حماية بيضاء)
bg_str = get_base64('background.jpg')
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_str if bg_str else ''}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    [data-testid="stElementToolbar"] {{ display: none; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: bold; background-color: #f8f9fa; border-radius: 5px; }}
    .stTabs [aria-selected="true"] {{ background-color: #007bff; color: white; }}
    </style>
""", unsafe_allow_html=True)

USER_CREDENTIALS = {"zaid": "11111"}

def show_logos(unique_key):
    """عرض الشعارات بشكل متوازن لتجنب أخطاء التكرار"""
    c_l, c_spacer, c_r = st.columns([1, 4, 1])
    with c_l:
        try: st.image("unicef_logo.png", width=130)
        except: st.write("UNICEF")
    with c_r:
        try: st.image("bdc_logo.png", width=130)
        except: st.write("BDC")
    st.divider()

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        show_logos("login_page")
        st.title("🔐 تسجيل الدخول")
        u = st.text_input("اسم المستخدم", key="u_login")
        p = st.text_input("كلمة المرور", type="password", key="p_login")
        if st.button("دخول"):
            if u in USER_CREDENTIALS and USER_CREDENTIALS[u] == p:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ البيانات غير صحيحة")
        return False
    return True

if check_password():
    show_logos("main_page")
    
    # --- جلب البيانات ---
    URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?download=1"

    @st.cache_data(ttl=600)
    def load_data():
        try:
            res = requests.get(URL)
            data = pd.read_excel(BytesIO(res.content))
            for col in data.columns:
                data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
            return data
        except: return None

    df = load_data()

    if df is not None:
        tab1, tab2, tab3 = st.tabs(["🔍 البحث", "📊 الإحصائيات", "🛡️ الأمن"])

        with tab1:
            st.subheader("🔍 محرك البحث الذكي")
            q = st.text_input("ابحث بالاسم، الرقم الفردي، أو الهاتف", key="search_q")
            if q:
                res_df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)]
                st.success(f"تم العثور على {len(res_df)} سجل")
                st.dataframe(res_df, use_container_width=True)
            else:
                st.dataframe(df.head(10), use_container_width=True)

        with tab2:
            st.subheader("📊 لوحة البيانات")
            c1, c2 = st.columns(2)
            with c1:
                if 'EmpGender' in df.columns:
                    st.write("**توزيع الجنس**")
                    g_data = df['EmpGender'].value_counts().reset_index()
                    g_data.columns = ['Gender', 'Count']
                    st.plotly_chart(px.pie(g_data, names='Gender', values='Count', hole=0.4), use_container_width=True)
            with c2:
                if 'Project' in df.columns:
                    st.write("**توزيع المشاريع**")
                    st.plotly_chart(px.pie(df, names='Project', hole=0.4), use_container_width=True)

        with tab3:
            st.subheader("🛡️ حالة النظام")
            st.info(f"إجمالي السجلات: {len(df)}")
            if st.button("🚪 تسجيل الخروج"):
                st.session_state["authenticated"] = False
                st.rerun()
        
        st.sidebar.title("⚙️ الإعدادات")
        if st.sidebar.button("🔄 تحديث البيانات"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("⚠️ فشل الاتصال بقاعدة البيانات")
