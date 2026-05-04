import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import re

st.set_page_config(page_title="مكتبة 313 - النسخ الدقيق", layout="centered")

st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; font-weight: bold; background-color: #1b5e20; color: white; height: 3.5em; }
    .stTextArea>div>div>textarea { font-size: 22px !important; direction: rtl; border: 2px solid #1b5e20; background-color: #fcfcfc; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 مكتبة 313 - نظام النسخ الذكي")

if "library" not in st.session_state:
    st.session_state.library = {}

with st.sidebar:
    st.header("إدارة المكتبة")
    new_files = st.file_uploader("ارفع كتب PDF", type="pdf", accept_multiple_files=True)
    if new_files:
        for f in new_files:
            if f.name not in st.session_state.library:
                st.session_state.library[f.name] = f.getvalue()
    
    all_books = list(st.session_state.library.keys())
    selected_book = st.selectbox("📖 اختر الكتاب:", all_books) if all_books else None

if selected_book:
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    page_key = f"page_{selected_book}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    current_idx = st.session_state[page_key]
    page = doc.load_page(current_idx)
    
    # تحسين جودة الصورة لضمان مطابقة النص
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    st.image(img, use_container_width=True)

    # --- التنقل ---
    st.write(f"<p style='text-align:center;'>الصفحة {current_idx + 1} من {doc.page_count}</p>", unsafe_allow_html=True)
    
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ السابقة", use_container_width=True):
            if current_idx > 0:
                st.session_state[page_key] -= 1
                st.rerun()
    with col_n:
        if st.button("التالية ➡️", use_container_width=True):
            if current_idx < doc.page_count - 1:
                st.session_state[page_key] += 1
                st.rerun()

    st.divider()
    
    # --- نظام النسخ الجزئي المطور ---
    st.subheader("🎯 حدد السطر المطلوب نسخه بدقة")
    
    # استخدام قيم افتراضية أصغر للقص لتسهيل التحديد
    t_val = st.slider("بداية السطر (%)", 0, 99, 45, key="t_v20")
    b_val = st.slider("نهاية السطر (%)", t_val + 1, 100, t_val + 5, key="b_v20")

    if st.button("✨ تنفيذ النسخ الجزئي"):
        try:
            # 1. عرض صورة القص للتأكد بصرياً
            w, h = img.size
            y0_img, y1_img = (t_val/100)*h, (b_val/100)*h
            crop = img.crop((0, y0_img, w, y1_img))
            st.image(crop, caption="هذا هو الجزء الذي سيتم تحويله لنص")
            
            # 2. استخراج النص باستخدام نظام "الكتل" (Blocks) لضمان الدقة
            # نقوم بحساب المنطقة في الـ PDF بناءً على النسب المئوية للسلايدر تماماً
            rect = fitz.Rect(0, (t_val/100)*page.rect.height, page.rect.width, (b_val/100)*page.rect.height)
            
            # استخراج النص من داخل هذا المستطيل حصراً
            text_parts = page.get_textbox(rect)
            
            # تنظيف النص
            clean_text = re.sub(r'[\u064B-\u0652\u0670]', '', text_parts).strip()
            
            if clean_text:
                st.success("تم النسخ بنجاح:")
                st.text_area("النص الجاهز:", value=clean_text, height=150)
            else:
                st.warning("لم يتم العثور على نص رقمي. إذا كان الكتاب (سكنر/صور)، يرجى التأكد من وضوح النص.")
                
        except Exception as e:
            st.error("حدث خطأ في المطابقة، يرجى إعادة المحاولة.")

else:
    st.info("ارفع ملفاتك من القائمة الجانبية.")
