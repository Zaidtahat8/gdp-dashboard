import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# إعدادات الصفحة المستقلة
st.set_page_config(page_title="سجل القائمة السوداء", layout="wide")

# تنسيق بصري تحذيري خاص بهذه الصفحة فقط
st.markdown("""
    <style>
    .stApp { background-color: #fff5f5; } 
    [data-testid="stElementToolbar"] { display: none; }
    .main-box { background-color: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    URL = "https://bdcjoorg-my.sharepoint.com/:x:/g/personal/zaltahat_bdc_org_jo/IQABP_FEs97DRZNQFxtFvyRGAe2xdQxDW6L3jTRC3S803SU?download=1"
    res = requests.get(URL)
    data = pd.read_excel(BytesIO(res.content))
    return data.astype(str)

df = load_data()

# محتوى الصفحة
st.error("🚫 سجل القائمة السوداء - إدارة مخيم الأزرق")
st.write("استخدم هذا المحرك للتحقق من الأسماء الممنوعة من التوظيف.")

# الكلمات المفتاحية التي تحدد القائمة السوداء في ملفك
bl_keywords = ['منقطع', 'انهاء', 'موقوف', 'blacklist']
blacklist_df = df[df['Notes'].str.contains('|'.join(bl_keywords), case=False, na=False)]

search_q = st.text_input("🔍 ابحث عن اسم أو رقم فردي في سجل المنع")

if search_q:
    results = blacklist_df[blacklist_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)]
    if not results.empty:
        st.warning(f"⚠️ تم العثور على {len(results)} سجل مطابق في القائمة السوداء!")
        st.dataframe(results.style.set_properties(**{'background-color': '#fee2e2', 'color': '#b91c1c'}), use_container_width=True)
    else:
        st.success("✅ الاسم غير مدرج في القائمة السوداء.")
else:
    st.dataframe(blacklist_df, use_container_width=True)
