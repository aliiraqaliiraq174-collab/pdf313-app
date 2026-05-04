import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import re

# إعداد الصفحة لتكون سريعة وخفيفة
st.set_page_config(page_title="مكتبة 313 الكبرى", layout="centered")

# تصميم الواجهة لتشبه التطبيقات الاحترافية
st.markdown("""
    <style>
    /* تصميم أزرار التنقل السفلية */
    .nav-btn { display: flex; justify-content: center; gap: 10px; padding: 10px; }
    .stButton>button { border-radius: 20px; font-weight: bold; transition: 0.3s; }
    .stTextArea>div>div>textarea { font-size: 20px !important; direction: rtl; border: 2px solid #1b5e20; }
    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] { width: 300px !important; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 مكتبة 313 الذكية")

# --- نظام رفع وإدارة أكثر من 100 كتاب ---
if "library" not in st.session_state:
    st.session_state.library = {} # مخزن الكتب

with st.sidebar:
    st.header("إدارة المكتبة")
    new_files = st.file_uploader("ارفع كتبك (PDF) - يمكنك رفع عدد غير محدود", type="pdf", accept_multiple_files=True)
    
    if new_files:
        for f in new_files:
            if f.name not in st.session_state.library:
                # تخزين مرجع الملف فقط لتوفير الذاكرة
                st.session_state.library[f.name] = f.getvalue()
        st.success(f"تمت إضافة {len(new_files)} كتاب بنجاح!")

    # اختيار الكتاب من قائمة منسدلة (لتجنب زحام الواجهة)
    all_books = list(st.session_state.library.keys())
    if all_books:
        selected_book = st.selectbox("📖 اختر الكتاب الذي تريد قراءته:", all_books)
    else:
        selected_book = None

# --- معالجة الكتاب المختار ---
if selected_book:
    # فتح الكتاب المختار فقط (توفير للرام)
    doc = fitz.open(stream=st.session_state.library[selected_book], filetype="pdf")
    
    # إدارة رقم الصفحة لكل كتاب بشكل مستقل
    page_key = f"page_{selected_book}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    # تحميل وعرض الصفحة
    current_idx = st.session_state[page_key]
    page = doc.load_page(current_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    st.image(img, use_container_width=True)

    # --- نظام التنقل المتطور (مثل المكتبة الشيعية) ---
    st.write(f"<h3 style='text-align:center;'>الصفحة {current_idx + 1} من {doc.page_count}</h3>", unsafe_allow_html=True)
    
    # حقل إدخال رقم الصفحة للذهاب السريع
    go_to = st.number_input("انتقل إلى صفحة:", min_value=1, max_value=doc.page_count, value=current_idx + 1)
    if go_to != current_idx + 1:
        st.session_state[page_key] = go_to - 1
        st.rerun()

    # أزرار التنقل الكبيرة
    col_p, col_n = st.columns(2
