import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import base64

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="نظام HR مخيم الأزرق 2026", layout="wide", page_icon="📝")

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# تحسين الـ CSS للخلفية ووضوح النصوص
bg_str = get_base64_of_bin_file('background.jpg')
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_str if bg_str else ''}");
        background-size: cover;
        background-attachment: fixed;
    }}
    /* طبقة تعتيم خفيفة لجعل الواجهة مريحة للعين */
    .main {{
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 20px;
    }}
    /* إخفاء أدوات الجدول للحماية */
    [data-testid="stElementToolbar"] {{ display: none; }}
    
    /* تنسيق العناوين والتبويبات */
    h1, h2, h3 {{ color: #004a99; font-family: 'Arial'; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ 
        background-color: #f8f9fa; 
        border-radius: 5px; 
        padding: 10px 20px;
        font-weight: bold;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #007bff; color: white; }}
    </style>
""", unsafe_allow_html=True)

USER_CREDENTIALS = {"zaid": "11111"}

def show_logos(key_suffix):
    """وظيفة لعرض الشعارين بشكل مرتب لتجنب خطأ التكرار"""
    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_l:
        try: st.image("unicef_logo.png", width=140)
        except: st.write("UNICEF Logo")
    with col_r:
        try: st.image("bdc_logo.png", width=140)
        except: st.write("BDC Logo")
    st.divider()

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        show_logos("login") # عرض الشعارات في صفحة الدخول
        st.title("🔐 تسجيل الدخول - نظام HR")
        user = st.text_input("اسم المستخدم", key="user_in")
        pw = st.text_input("كلمة المرور", type="password", key="pw_in")
        if st.button("دخول"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pw:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ البيانات غير صحيحة")
        return False
    return True

if check_password():
    show_logos("main") # عرض الشعارات في الصفحة الرئيسية
    
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
        tab1, tab2, tab3 = st.tabs(["🔍 البحث والتدقيق", "📊 الإحصائيات", "⚙️ الإعدادات"])

        with tab1:
            st.subheader("🔍 محرك البحث الذكي")
            search_query = st.text_input("ابحث بالاسم، الرقم الفردي، أو الهاتف", key="search_box")
            
            if search_query:
                filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
                st.success(f"تم العثور على {len(filtered_df)} سجل")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df.head(10), use_container_width=True)

        with tab2:
            st.subheader("📊 لوحة تحكم البيانات")
            c1, c2 = st.columns(2)
            with c1:
                if 'EmpGender' in df.columns:
                    st.markdown("**توزيع الجنس**")
                    g_data = df['EmpGender'].value_counts().reset_index()
                    g_data.columns = ['Gender', 'Count']
                    fig = px.pie(g_data, names='Gender', values='Count', color='Gender',
                                color_discrete_map={'Male':'#3498db','Female':'#e91e63'}, hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if 'Project' in df.columns:
                    st.markdown("**توزيع المشاريع**")
                    fig_p = px.pie(df, names='Project', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_p, use_container_width=True)

        with tab3:
            st.subheader("⚙️ خيارات النظام")
            st.info("النظام يعمل بأمان والقاعدة متصلة بـ SharePoint")
            if st.button("🚪 تسجيل الخروج"):
                st.session_state["authenticated"] = False
                st.rerun()

        st.sidebar.image("bdc_logo.png", width=100) if bg_str else None
        if st.sidebar.button("🔄 تحديث البيانات"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("⚠️ فشل في تحميل البيانات")خط فاصل بين الشعارين وعنوان النظام

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
