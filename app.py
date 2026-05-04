import streamlit as st
import fitz  # مكتبة PyMuPDF القوية جداً
from PIL import Image
import io

st.set_page_config(page_title="مكتبة مهدي الاحترافية", layout="wide")

st.title("📚 مكتبة مهدي الذكية (الإصدار الاحترافي)")

# رفع الكتب (تتحمل عدد غير محدود)
uploaded_files = st.sidebar.file_uploader("ارفع كتب PDF هنا", accept_multiple_files=True)

if uploaded_files:
    # اختيار الكتاب من القائمة
    book_names = [f.name for f in uploaded_files]
    selected_book_name = st.sidebar.selectbox("اختر الكتاب للقراءة", book_names)
    
    # الحصول على الملف المختار
    for f in uploaded_files:
        if f.name == selected_book_name:
            file_data = f.read()
            doc = fitz.open(stream=file_data, filetype="pdf")
            
            # التحكم بالصفحات
            page_num = st.sidebar.number_input(f"الصفحة (من {doc.page_count})", min_value=1, max_value=doc.page_count, step=1)
            
            # عرض الصفحة
            page = doc.load_page(page_num - 1)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # دقة عالية جداً
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            st.image(img, caption=f"الصفحة: {page_num}", use_container_width=True)
            
            # ميزة النسخ الاحترافية (بدون تقطيع)
            if st.button("✨ استخراج النص للنسخ (بدون حركات)"):
                text = page.get_text("text")
                # تنظيف النص من الحركات (الفتحة والكسرة) ليكون النسخ صافي
                import re
                clean_text = re.sub(r'[\u064B-\u0652\u0670]', '', text)
                
                st.subheader("النص المستخرج:")
                st.text_area("انسخ من هنا:", value=clean_text, height=300)
                st.success("تم استخراج النص بدقة عالية!")

else:
    st.info("قم برفع الكتب من القائمة الجانبية للبدء.")
