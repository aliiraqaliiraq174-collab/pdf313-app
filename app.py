import streamlit as st
import fitz
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
import numpy as np
import cv2
import easyocr

st.set_page_config(page_title="مكتبة 313 - دقة السكنر", layout="centered")

@st.cache_resource
def load_ocr():
    # تحميل محرك اللغة العربية مع خاصية التعرف على الأرقام والرموز
    return easyocr.Reader(['ar'])

reader = load_ocr()

# التصميم الزخرفي (بدون التأثير على الأداء)
st.markdown("""
    <style>
    .main { background-color: #f4f1ea; }
    h1 { color: #1b5e20; text-align: center; border-bottom: 2px solid #d4af37; font-family: 'Amiri', serif; }
    .stButton>button { background-color: #1b5e20; color: #d4af37; border: 2px solid #d4af37; font-weight: bold; border-radius: 10px; }
    .stTextArea>div>div>textarea { font-size: 24px !important; direction: rtl; border: 2px solid #1b5e20; background-color: #fffdf5; }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>﷽</h1>", unsafe_allow_html=True)
st.title("مكتبة 313 - النسخ الاحترافي للسكنر")

if "library" not in st.session_state:
    st.session_state.library = {}

with st.sidebar:
    st.header("📚 الكتب المرفوعة")
    files = st.file_uploader("ارفع كتب السكنر (PDF)", type="pdf", accept_multiple_files=True)
    if files:
        for f in files:
            if f.name not in st.session_state.library:
                st.session_state.library[f.name] = f.getvalue()
    selected_book = st.selectbox("اختر الكتاب:", list(st.session_state.library.keys())) if st.session_state.library else None

if selected_book:
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    p_key = f"p_{selected_book}"
    if p_key not in st.session_state: st.session_state[p_key] = 0
    
    idx = st.session_state[p_key]
    page = doc.load_page(idx)
    
    # تحويل الصفحة لصورة بجودة عالية جداً للتعامل مع السكنر
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    st.image(img, use_container_width=True)

    # التنقل
    st.write(f"<p style='text-align:center;'>الصفحة {idx + 1} من {doc.page_count}</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ السابقة"):
            if idx > 0: st.session_state[p_key] -= 1; st.rerun()
    with c2:
        if st.button("التالية ➡️"):
            if idx < doc.page_count - 1: st.session_state[p_key] += 1; st.rerun()

    st.divider()

    # --- معالجة النسخ للسكنر ---
    st.subheader("🖋️ استخراج النص من الصورة")
    t_v = st.slider("حدد بداية السطر", 0, 95, 45)
    b_v = st.slider("حدد نهاية السطر", t_v + 1, 100, t_v + 8)

    w, h = img.size
    crop = img.crop((0, (t_v/100)*h, w, (b_v/100)*h))
    
    # --- سر الدقة العالية (المعالجة البصرية قبل النسخ) ---
    # تحويل الصورة لرمادي لزيادة التركيز
    enhancer = ImageEnhance.Contrast(crop)
    crop_enhanced = enhancer.enhance(2.0) # مضاعفة التباين
    sharpener = ImageEnhance.Sharpness(crop_enhanced)
    crop_final = sharpener.enhance(2.0) # زيادة حدة الحروف
    
    st.image(crop_final, caption="المعاينة المحسنة (هكذا يراها التطبيق بوضوح)")

    if st.button("✨ نسخ النص الآن"):
        with st.spinner("جاري تحليل صورة السكنر بدقة عالية..."):
            try:
                # تحويل الصورة لـ Numpy Array ليفهمها المحرك
                img_np = np.array(crop_final.convert('RGB'))
                
                # تنفيذ القراءة مع تفعيل تحسينات الحواف
                results = reader.readtext(img_np, detail=0, paragraph=True, contrast_ths=0.1, adjust_contrast=0.7)
                
                if results:
                    final_text = " ".join(results)
                    # تنظيف النص من التشكيل المزعج للنسخ
                    clean_text = re.sub(r'[\u064B-\u0652\u0670]', '', final_text).strip()
                    
                    st.success("تم استخراج النص بفضل الله:")
                    st.text_area("انسخ النص المستخرج:", value=clean_text, height=200)
                else:
                    st.warning("النص غير واضح، حاول تكبير المنطقة قليلاً.")
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
else:
    st.info("ارفع كتب السكنر من الجانب للبدء.")
