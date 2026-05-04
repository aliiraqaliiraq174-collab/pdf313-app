import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import re

st.set_page_config(page_title="مكتبة 313 الاحترافية", layout="centered")

# تنسيق CSS لجعل الواجهة أجمل
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1b5e20; color: white; }
    .stTextArea>div>div>textarea { font-size: 20px !important; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 مكتبة 313 - النسخ الجزئي")

# رفع الكتب
uploaded_file = st.sidebar.file_uploader("ارفع كتاب PDF", type="pdf")

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    # إدارة حالة الصفحات
    if 'page_count' not in st.session_state:
        st.session_state.page_count = 0

    # عرض الكتاب
    page = doc.load_page(st.session_state.page_count)
    
    # تحويل الصفحة لصورة بدقة عالية للقص
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    # عرض الصفحة الحالية
    st.image(img, use_container_width=True)

    # --- التحكم في الأسفل (التنقل) ---
    st.write(f"**الصفحة {st.session_state.page_count + 1} من {doc.page_count}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ الصفحة السابقة"):
            if st.session_state.page_count > 0:
                st.session_state.page_count -= 1
                st.rerun()
    with col2:
        if st.button("الصفحة التالية ➡️"):
            if st.session_state.page_count < doc.page_count - 1:
                st.session_state.page_count += 1
                st.rerun()

    # --- نظام النسخ الجزئي المتطور ---
    st.divider()
    st.subheader("🎯 منطقة النسخ الجزئي")
    st.info("حدد بدقة من أين يبدأ وأين ينتهي السطر الذي تريده:")
    
    # منزلقات لتحديد المنطقة (النسخ الجزئي)
    col_a, col_b = st.columns(2)
    with col_a:
        top = st.slider("من الأعلى (بداية السطر)", 0, 100, 20)
    with col_b:
        bottom = st.slider("إلى الأسفل (نهاية السطر)", 0, 100, 30)

    if st.button("✨ استخراج النص المحدد فقط"):
        # حساب إحداثيات القص
        width, height = img.size
        y0 = (top / 100) * height
        y1 = (bottom / 100) * height
        
        # قص المنطقة المحددة برمجياً
        crop_img = img.crop((0, y0, width, y1))
        st.image(crop_img, caption="المنطقة التي حددتها")
        
        # استخراج النص من المنطقة المحددة فقط
        rect = fitz.Rect(0, (top/100)*page.rect.height, page.rect.width, (bottom/100)*page.rect.height)
        text = page.get_text("text", clip=rect)
        
        # تنظيف النص من التشكيل لضمان النسخ الصافي
        clean_text = re.sub(r'[\u064B-\u0652\u0670]', '', text)
        
        if clean_text.strip():
            st.success("تم استخراج النص الجزئي بنجاح:")
            st.text_area("انسخ السطر من هنا:", value=clean_text, height=150)
        else:
            st.warning("لم يتم العثور على نص في هذه المنطقة، جرب تغيير أرقام التحديد.")

else:
    st.info("أهلاً بك في مكتبة 313. يرجى رفع ملف PDF من القائمة الجانبية للبدء.")
