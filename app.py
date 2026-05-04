import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import re

# إعداد الصفحة لتكون سريعة وخفيفة
st.set_page_config(page_title="مكتبة 313 الكبرى", layout="centered")

# تصميم الواجهة
st.markdown("""
    <style>
    .stButton>button { border-radius: 20px; font-weight: bold; transition: 0.3s; height: 3.5em; }
    .stTextArea>div>div>textarea { font-size: 20px !important; direction: rtl; border: 2px solid #1b5e20; }
    section[data-testid="stSidebar"] { width: 300px !important; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 مكتبة 313 الذكية")

# --- نظام إدارة المكتبة ---
if "library" not in st.session_state:
    st.session_state.library = {}

with st.sidebar:
    st.header("إدارة المكتبة")
    new_files = st.file_uploader("ارفع كتبك (PDF) - عدد غير محدود", type="pdf", accept_multiple_files=True)
    
    if new_files:
        for f in new_files:
            if f.name not in st.session_state.library:
                st.session_state.library[f.name] = f.getvalue()
        st.success(f"تمت إضافة الكتب بنجاح!")

    all_books = list(st.session_state.library.keys())
    selected_book = st.selectbox("📖 اختر الكتاب للقراءة:", all_books) if all_books else None

# --- عرض ومعالجة الكتاب ---
if selected_book:
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    
    page_key = f"page_{selected_book}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    current_idx = st.session_state[page_key]
    page = doc.load_page(current_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    st.image(img, use_container_width=True)

    # --- نظام التنقل السفلي المتطور ---
    st.write(f"<h3 style='text-align:center;'>الصفحة {current_idx + 1} من {doc.page_count}</h3>", unsafe_allow_html=True)
    
    # الانتقال السريع برقم الصفحة
    go_to = st.number_input("انتقل إلى صفحة مباشرة:", min_value=1, max_value=doc.page_count, value=current_idx + 1)
    if go_to != current_idx + 1:
        st.session_state[page_key] = go_to - 1
        st.rerun()

    # أزرار التنقل (تم إصلاح القوس هنا)
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ الصفحة السابقة", use_container_width=True):
            if current_idx > 0:
                st.session_state[page_key] -= 1
                st.rerun()
    with col_n:
        if st.button("الصفحة التالية ➡️", use_container_width=True):
            if current_idx < doc.page_count - 1:
                st.session_state[page_key] += 1
                st.rerun()

    # --- أداة النسخ الجزئي ---
    st.divider()
    st.subheader("🎯 أداة النسخ الجزئي")
    
    t_val = st.slider("بداية السطر (%)", 0, 95, 20, key="t_slider")
    b_val = st.slider("نهاية السطر (%)", t_val + 1, 100, t_val + 10, key="b_slider")

    if st.button("✨ نسخ النص من المنطقة المحددة"):
        try:
            w, h = img.size
            crop = img.crop((0, (t_val/100)*h, w, (b_val/100)*h))
            st.image(crop, caption="معاينة الجزء المحدد")
            
            rect = fitz.Rect(0, (t_val/100)*page.rect.height, page.rect.width, (b_val/100)*page.rect.height)
            raw_text = page.get_text("text", clip=rect)
            clean_text = re.sub(r'[\u064B-\u0652\u0670]', '', raw_text).strip()
            
            if clean_text:
                st.success("تم استخراج النص بنجاح:")
                st.text_area("انسخ السطر:", value=clean_text, height=150)
            else:
                st.warning("المنطقة المختارة لا تحتوي على نص رقمي واضح.")
        except Exception as e:
            st.error("حدث خطأ أثناء القص، يرجى المحاولة مرة أخرى.")

else:
    st.info("ارفع الكتب من القائمة الجانبية لتظهر لك هنا.")
