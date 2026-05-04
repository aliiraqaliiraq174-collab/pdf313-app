import streamlit as st
import fitz
from PIL import Image, ImageOps, ImageEnhance
import io
import re
import numpy as np
import cv2 # لإضافة المعالجة الرقمية القوية
import easyocr

st.set_page_config(page_title="مكتبة 313 - النسخة الأسطورية", layout="centered")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ar'])

reader = load_ocr()

st.title("📚 مكتبة 313 - الحل النهائي والأقوى")

if "library" not in st.session_state:
    st.session_state.library = {}

with st.sidebar:
    st.header("المخزن")
    files = st.file_uploader("ارفع كتب PDF", type="pdf", accept_multiple_files=True)
    if files:
        for f in files:
            if f.name not in st.session_state.library:
                st.session_state.library[f.name] = f.getvalue()
    selected_book = st.selectbox("اختر كتابك:", list(st.session_state.library.keys())) if st.session_state.library else None

if selected_book:
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    p_key = f"p_{selected_book}"
    if p_key not in st.session_state: st.session_state[p_key] = 0
    
    idx = st.session_state[p_key]
    page = doc.load_page(idx)
    
    # تحويل الصفحة لصورة بجودة 300 DPI
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    st.image(img, use_container_width=True)

    # أزرار التنقل السفلية
    st.write(f"<p style='text-align:center;'>الصفحة {idx + 1} من {doc.page_count}</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ السابقة", use_container_width=True):
            if idx > 0: st.session_state[p_key] -= 1; st.rerun()
    with c2:
        if st.button("التالية ➡️", use_container_width=True):
            if idx < doc.page_count - 1: st.session_state[p_key] += 1; st.rerun()

    st.divider()

    st.subheader("🎯 منطقة النسخ العميقة")
    t_v = st.slider("من الأعلى (%)", 0, 95, 45)
    b_v = st.slider("إلى الأسفل (%)", t_v + 1, 100, t_v + 10)

    # مقص المعاينة
    w, h = img.size
    crop = img.crop((0, (t_v/100)*h, w, (b_v/100)*h))
    
    # --- المعالجة الرقمية (السر الحقيقي للقوة) ---
    # تحويل الصورة إلى OpenCV لعمل سحر المعالجة
    open_cv_image = np.array(crop.convert('RGB'))
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY) # تحويل لرمادي
    # تصفية الضوضاء وزيادة حدة الحروف (Thresholding)
    processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    st.image(processed_img, caption="هكذا يرى الذكاء الاصطناعي النص الآن (أوضح وأدق)")

    if st.button("🚀 تنفيذ أقوى نسخ مجاني"):
        with st.spinner("جاري التحليل العميق..."):
            try:
                # القراءة من الصورة المعالجة رقمياً
                results = reader.readtext(processed_img, detail=0)
                clean = re.sub(r'[\u064B-\u0652\u0670]', '', " ".join(results)).strip()
                
                if clean:
                    st.success("تم النسخ بنجاح!")
                    st.text_area("النص المستخرج:", value=clean, height=180)
                else:
                    st.warning("لم نتمكن من القراءة، جرب تعديل منطقة القص.")
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
else:
    st.info("ارفع كتبك للبدء.")
