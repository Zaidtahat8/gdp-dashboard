import pandas as pd
import streamlit as st
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة متطوعي مخيم الأزرق", layout="wide", page_icon="📊")

st.title("📊 نظام إدارة وأرشفة سجلات المتطوعين - التطوير الذكي")
st.markdown("---")

# 1. تحميل الملف
uploaded_file = st.file_uploader("يرجى رفع ملف الإكسل (Excel)", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # تنظيف البيانات الأساسية وتحويل المعرفات إلى نصوص
        id_cols = ['Individual Number', 'الرقم الأمني', 'EmpNo', 'Case Number', 'رقم الهاتف']
        for col in id_cols:
            if col in df.columns:
                # تحويل إلى نص، إزالة الكسور، وإزالة المسافات
                df[col] = df[col].astype(str).str.replace('.0', '', regex=False).str.strip()

        # --- لوحة الإحصائيات العامة (Dashboard) ---
        st.subheader("📈 نظرة عامة على القوى العاملة")
        
        total_contracts = len(df)
        unique_volunteers = df['Individual Number'].nunique()
        active_projects = df['Project'].nunique()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي العقود المسجلة", total_contracts)
        m2.metric("عدد المتطوعين (بدون تكرار)", unique_volunteers)
        m3.metric("عدد المشاريع النشطة", active_projects)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### توزيع المتطوعين حسب المشروع")
            project_counts = df.groupby('Project')['Individual Number'].nunique().reset_index()
            fig_proj = px.bar(project_counts, x='Project', y='Individual Number', 
                              labels={'Individual Number': 'عدد المتطوعين'},
                              color='Project', template="seaborn")
            st.plotly_chart(fig_proj, use_container_width=True)
        with c2:
            st.markdown("#### توزيع الجنسين (Gender)")
            if 'EmpGender' in df.columns:
                gender_counts = df['EmpGender'].value_counts().reset_index()
                fig_gen = px.pie(gender_counts, names='EmpGender', values='count', 
                                 hole=0.4, template="seaborn")
                st.plotly_chart(fig_gen, use_container_width=True)

        st.markdown("---")

        # --- الخطوة الثانية: نظام البحث المطور ---
        st.subheader("🔍 البحث الشامل عن متطوع")
        
        # تقسيم البحث إلى 4 خانات
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            search_id = st.text_input("الرقم الفردي/الأمني:")
        with s2:
            search_case = st.text_input("رقم الحالة (Case No):")
        with s3:
            search_phone = st.text_input("رقم الهاتف:")
        with s4:
            search_name = st.text_input("الاسم (عربي/إنجليزي):")

        # منطق البحث المتعدد
        query = pd.DataFrame() # إنشاء إطار بيانات فارغ للنتائج
        
        if search_id:
            query = df[(df['Individual Number'] == search_id) | (df['الرقم الأمني'] == search_id)]
        elif search_case:
            query = df[df['Case Number'] == search_case]
        elif search_phone:
            query = df[df['رقم الهاتف'] == search_phone]
        elif search_name:
            query = df[(df['Name'].str.contains(search_name, na=False)) | (df['En Full Name'].str.contains(search_name, na=False, case=False))]

        # عرض النتائج
        if not query.empty:
            latest_record = query.iloc[-1]
            
            with st.expander(f"✅ تم العثور على {len(query)} سجلات - انقر للتفاصيل", expanded=True):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.info(f"**الاسم:**\n\n{latest_record['Name']}")
                    st.write(f"**رقم الحالة:** {latest_record['Case Number']}")
                with col_b:
                    st.info(f"**الموقع الحالي:**\n\n{latest_record['Centre']}")
                    st.write(f"**رقم الهاتف:** {latest_record['رقم الهاتف']}")
                with col_c:
                    st.info(f"**تاريخ آخر تعيين:**\n\n{latest_record['Start Date']}")
                    st.write(f"**إجمالي العقود السابقة:** {len(query)}")

                st.markdown("#### 📜 التاريخ الوظيفي التفصيلي")
                # عرض الأعمدة الأساسية التي تهمك في القراءة التاريخية
                display_columns = [
                    'Project', 'Main Position', 'Centre', 'Start Date', 
                    'Contract End Date', 'the Actual end contract', 'Net Salary', 'Notes'
                ]
                # عرض الجدول بشكل مرتب
                st.table(query[display_columns])

        elif any([search_id, search_case, search_phone, search_name]):
            st.error("❌ لم يتم العثور على أي سجلات مطابقة للبيانات المدخلة.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
else:
    st.info("💡 يرجى رفع ملف الإكسل لبدء عملية الفرز والبحث.")