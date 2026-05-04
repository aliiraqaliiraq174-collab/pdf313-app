import streamlit as st
import fitz
from PIL import Image, ImageOps, ImageEnhance
import io
import re
import numpy as np
import cv2
import easyocr

# إعداد الصفحة بتصميم إسلامي
st.set_page_config(page_title="مكتبة 313 - الإصدار الاحترافي", layout="centered")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ar'])

reader = load_ocr()

# تصميم واجهة مزخرفة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&display=swap');
    
    .main { background-color: #f4f1ea; }
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/islamic-art.png");
    }
    
    h1 { font-family: 'Amiri', serif; color: #1b5e20; text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 10px; }
    
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        height: 3.5em;
        background-color: #1b5e20;
        color: #d4af37;
        font-weight: bold;
        border: 2px solid #d4af37;
        font-family: 'Amiri', serif;
        font-size: 20px;
    }
    
    .stTextArea>div>div>textarea {
        font-size: 24px !important;
        direction: rtl;
        border: 2px solid #d4af37;
        background-color: #fffdf5;
        font-family: 'Amiri', serif;
    }
    
    .css-1kyx0rg { background-color: #1b5e20 !important; } /* جانب المكتبة */
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>﷽</h1>", unsafe_allow_html=True)
st.title("مكتبة 313 الإلكترونية")

if "library" not in st.session_state:
    st.session_state.library = {}

with st.sidebar:
    st.markdown("<h2 style='color:#1b5e20;'>خزانة الكتب</h2>", unsafe_allow_html=True)
    files = st.file_uploader("ارفع المخطوطات والكتب", type="pdf", accept_multiple_files=True)
    if files:
        for f in files:
            if f.name not in st.session_state.library:
                st.session_state.library[f.name] = f.getvalue()
    selected_book = st.selectbox("اختر كتاباً للمطالعة:", list(st.session_state.library.keys())) if st.session_state.library else None

if selected_book:
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    p_key = f"p_{selected_book}"
    if p_key not in st.session_state: st.session_state[p_key] = 0
    
    idx = st.session_state[p_key]
    page = doc.load_page(idx)
    
    # رفع الدقة إلى 4X لضمان عدم ضياع أي حرف
    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    st.image(img, use_container_width=True)

    # أزرار التنقل المزخرفة
    st.write(f"<p style='text-align:center; font-family:Amiri; font-size:22px; color:#1b5e20;'><b>الصحيفة {idx + 1} من {doc.page_count}</b></p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚜️ السابقة"):
            if idx > 0: st.session_state[p_key] -= 1; st.rerun()
    with c2:
        if st.button("التالية ⚜️"):
            if idx < doc.page_count - 1: st.session_state[p_key] += 1; st.rerun()

    st.divider()

    # --- منطقة النسخ الفائق ---
    st.subheader("🖋️ استخراج النص الشريف")
    t_v = st.slider("تحديد بداية السطر", 0, 95, 45)
    b_v = st.slider("تحديد نهاية السطر", t_v + 1, 100, t_v + 5)

    w, h = img.size
    crop = img.crop((0, (t_v/100)*h, w, (b_v/100)*h))
    
    # --- سر الـ 100% دقة: المعالجة الثلاثية ---
    img_np = np.array(crop.convert('RGB'))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # تحسين التباين (Contrast) لجعل الحروف الباهتة قوية
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_gray = clahe.apply(gray)
    
    # تصفية الضوضاء وتقوية الحواف (Denoising)
    dst = cv2.fastNlMeansDenoising(enhanced_gray, None, 10, 7, 21)
    
    # التحويل الثنائي الذكي (Adaptive Thresholding)
    # هذا يجعل الحروف تبرز حتى لو كانت في منطقة مظلمة
    final_img = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    st.image(final_img, caption="المعاينة المجهرية للنص")

    if st.button("✨ استنساخ النص بالدقة الكاملة"):
        with st.spinner("جاري تحليل الحروف والكلمات..."):
            try:
                # القراءة بمحرك EasyOCR مع تفعيل خاصيةparagraph لربط الكلمات المفقودة
                results = reader.readtext(final_img, detail=0, paragraph=True)
                clean = " ".join(results)
                # إزالة الحركات لضمان النسخ الصافي
                clean = re.sub(r'[\u064B-\u0652\u0670]', '', clean).strip()
                
                if clean:
                    st.success("تم استخراج النص بفضل الله:")
                    st.text_area("", value=clean, height=200)
                else:
                    st.warning("لم يظهر نص، حاول توسيع منطقة التحديد قليلاً.")
            except Exception as e:
                st.error(f"عذراً، حدث خطأ: {str(e)}")
else:
    st.info("ارفع كتبك الدينية لتبدأ مكتبتك الخاصة.")
