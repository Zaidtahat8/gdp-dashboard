import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="سجل المتقدمين للوظائف", layout="wide", page_icon="📄")

# --- 2. تحسين المظهر (نفس هوية النظام) ---
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] { display: none; }
    .main { background-color: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# عرض الشعارات إذا رغبت (اختياري)
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    try: st.image("unicef_logo.png", width=130)
    except: pass
with c3:
    try: st.image("bdc_logo.png", width=130)
    except: pass
st.divider()

# --- 3. جلب بيانات قاعدة المتقدمين ---
@st.cache_data(ttl=600)
def load_applicants_data():
    # ⚠️ تنبيه هام: قم باستبدال هذا الرابط برابط SharePoint الخاص بملف إكسل "المتقدمين" ⚠️
    URL = "ضع_رابط_ملف_المتقدمين_هنا_بين_علامتي_التنصيص"
    
    try:
        res = requests.get(URL)
        data = pd.read_excel(BytesIO(res.content))
        # تنظيف البيانات
        for col in data.columns:
            data[col] = data[col].astype(str).str.replace('.0', '', regex=False).str.strip()
        return data
    except:
        return None

st.title("📂 قاعدة بيانات المتقدمين للوظائف")
st.info("استخدم هذا المحرك للبحث عن السير الذاتية وبيانات الأشخاص الذين تقدموا للعمل.")

applicants_df = load_applicants_data()

if applicants_df is not None:
    # --- 4. محرك البحث الخاص بالمتقدمين ---
    search_q = st.text_input("🔍 ابحث بالاسم، التخصص، أو رقم الهاتف للمتقدمين", key="applicant_search")
    
    if search_q:
        # فلترة البيانات بناءً على البحث
        results = applicants_df[applicants_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)]
        st.success(f"تم العثور على {len(results)} سيرة ذاتية مطابقة")
        st.dataframe(results, use_container_width=True)
    else:
        st.write("📌 عرض أحدث المتقدمين للوظائف:")
        st.dataframe(applicants_df.head(20), use_container_width=True)
else:
    if "ضع_رابط_ملف_المتقدمين_هنا_بين_علامتي_التنصيص" in load_applicants_data.__code__.co_consts:
         st.warning("💡 يرجى إضافة رابط ملف الإكسل الخاص بالمتقدمين داخل الكود لكي تظهر البيانات.")
    else:
         st.error("⚠️ فشل في الاتصال بقاعدة بيانات المتقدمين. يرجى التأكد من الرابط.")
