import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import base64

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="نظام HR مخيم الأزرق 2026", layout="wide", page_icon="📝")

# وظيفة لتحويل صورة الخلفية المحلية إلى Base64 لتعمل كخلفية للصفحة
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- إضافة الخلفية وتحسين مظهر التبويبات عبر CSS ---
# ملاحظة: تأكد من وجود ملف 'background.jpg' في GitHub لتفعيل الخلفية
bg_str = get_base64_of_bin_file('background.jpg')
if bg_str:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* تحسين مظهر الحاويات لتكون مقروءة فوق الخلفية (شفافية بيضاء) */
        [data-testid="stVerticalBlock"] > div {{
            background-color: rgba(255, 255, 255, 0.88); 
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        [data-testid="stElementToolbar"] {{ display: none; }} /* إخفاء أدوات الجدول للحماية */
        .stTabs [data-baseweb="tab-list"] {{ gap: 15px; }}
        .stTabs [data-baseweb="tab"] {{ height: 50px; background-color: #f0f2f6; border-radius: 5px; font-weight: bold; }}
        .stTabs [aria-selected="true"] {{ background-color: #007bff; color: white; }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # تنسيقات أساسية في حال عدم وجود خلفية
    st.markdown("""<style>[data-testid="stElementToolbar"] { display: none; }</style>""", unsafe_allow_html=True)


USER_CREDENTIALS = {"zaid": "11111"}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        # --- إضافة الشعارين في صفحة تسجيل الدخول أيضاً لمظهر احترافي ---
        col_log_l, col_log_c, col_log_r = st.columns([1, 2, 1])
        with col_log_l:
            try: st.image("unicef_logo.png", width=150)
            except: pass
        with col_log_r:
            try: st.image("bdc_logo.png", width=150)
            except: pass
            
        st.title("🔐 تسجيل الدخول - نظام HR الأزرق")
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
    # --- 2. إضافة الشعارين في أعلى الصفحة الرئيسية بعد الدخول ---
    # ننشئ 3 أعمدة: الأول للشعار الأيسر (UNICEF)، الثاني فارغ (مساحة)، والثالث للشعار الأيمن (BDC)
    col_unicef, col_spacer, col_bdc = st.columns([1.5, 5, 1.5])
    
    with col_unicef:
        try:
            # شعار UNICEF على اليسار ( width=200 للحجم المناسب)
            st.image("unicef_logo.png", width=200)
        except:
            st.error("💡 تأكد من رفع 'unicef_logo.png' على GitHub")
            
    with col_bdc:
        try:
            # شعار BDC على اليمين ( width=200 للحجم المناسب)
            st.image("bdc_logo.png", width=200)
        except:
            st.error("💡 تأكد من رفع 'bdc_logo.png' على GitHub")

    st.divider() # خط فاصل بين الشعارين وعنوان النظام

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
