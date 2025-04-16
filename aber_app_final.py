import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="عابر", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #000000;
            color: #ffffff;
        }
        .stApp {
            background-color: #000000;
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff;
            color: #000000;
        }
        .stButton>button {
            background-color: #198754;
            color: white;
        }
        .css-1d391kg {
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# حالة البرنامج للتنقل بين الخطوات
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "phone_number" not in st.session_state:
    st.session_state.phone_number = ""
if "destination" not in st.session_state:
    st.session_state.destination = ""
if "user_type" not in st.session_state:
    st.session_state.user_type = ""
if "hour" not in st.session_state:
    st.session_state.hour = datetime.now().hour
if "chosen_path" not in st.session_state:
    st.session_state.chosen_path = ""

# بيانات الزحمة الأساسية
traffic_data = {
    "main": {"name": "الطريق الرئيسي", "base_traffic": 75, "length_km": 10},
    "alt": {"name": "الطريق البديل", "base_traffic": 45, "length_km": 13}
}

# دالة التنبؤ بالزحمة
def predict_traffic(base, hour):
    if 6 <= hour <= 9:
        return base + 20
    elif 16 <= hour <= 18:
        return base + 15
    elif 12 <= hour <= 13:
        return base + 5
    else:
        return base

# الخطوة 1: تسجيل المستخدم
if st.session_state.step == 1:
    st.title("مرحبًا بك في عابر")
    st.subheader("فضلاً أدخل بياناتك للمتابعة")
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الجوال")

    if st.button("التالي"):
        if name and phone:
            st.session_state.user_name = name
            st.session_state.phone_number = phone
            st.session_state.step = 2
        else:
            st.warning("يرجى تعبئة جميع الحقول")

# الخطوة 2: اختيار بيانات الرحلة
elif st.session_state.step == 2:
    st.title("خطط رحلتك")
    destination = st.text_input("وجهتك")
    user_type = st.selectbox("نوع الرحلة", ["عادي", "مستعجل", "مهتم بتقليل الوقود"])
    hour = st.slider("وقت الخروج المتوقع", 0, 23, st.session_state.hour)

    if st.button("تحليل الزحمة"):
        if destination:
            st.session_state.destination = destination
            st.session_state.user_type = user_type
            st.session_state.hour = hour
            st.session_state.step = 3
        else:
            st.warning("يرجى إدخال وجهتك")

# الخطوة 3: تحليل الزحمة وتقديم الخيارات
elif st.session_state.step == 3:
    st.title("نتائج التحليل")

    main_pred = predict_traffic(traffic_data["main"]["base_traffic"], st.session_state.hour)
    alt_pred = predict_traffic(traffic_data["alt"]["base_traffic"], st.session_state.hour)

    st.write(f"الطريق الرئيسي: {main_pred}% ازدحام - {traffic_data['main']['length_km']} كم")
    st.write(f"الطريق البديل: {alt_pred}% ازدحام - {traffic_data['alt']['length_km']} كم")

    st.caption("جميع بيانات الزحام مبنية على تحليلات مسبقة لأيام وأوقات مماثلة، وليست عرضًا مباشرًا للحركة المرورية.")

    st.markdown("### اختر الطريق الذي تود سلوكه:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("اختيار الطريق الرئيسي"):
            st.session_state.chosen_path = "main"
            st.session_state.step = 4
    with col2:
        if st.button("اختيار الطريق البديل"):
            st.session_state.chosen_path = "alt"
            st.session_state.step = 4

# الخطوة 4: عرض الخريطة الواقعية
elif st.session_state.step == 4:
    st.title("خريطة الطريق المختار")

    path = st.session_state.chosen_path
    path_name = traffic_data[path]["name"]
    traffic_level = predict_traffic(traffic_data[path]["base_traffic"], st.session_state.hour)

    st.write(f"تم اختيار: {path_name}")
    st.write(f"نسبة الزحمة: {traffic_level}%")

    # إعداد الخريطة
m = folium.Map(location=[17.5651, 44.2289], zoom_start=13)

# إضافة العلامات (Markers)
folium.Marker([17.5651, 44.2289], tooltip="الموقع 1").add_to(m)
folium.Marker([17.5700, 44.2300], tooltip="الموقع 2").add_to(m)

# تحديد لون الطريق حسب الزحمة
traffic_level = 80  # قيمة مؤقتة للتجربة
color = "red" if traffic_level > 70 else "green"

# رسم الطريق (خط بين نقطتين)
path_name = st.session_state.chosen_path
folium.PolyLine(
    locations=[[17.5651, 44.2289], [17.5700, 44.2300]],
    tooltip=path_name,
    color=color,
    weight=6
).add_to(m)

# عرض الخريطة داخل تطبيق Streamlit
if st.session_state.step == 4:
    st_folium(m, width=700, height=500)
    st.success("نتمنى لكِ رحلة آمنة!")
# رسالة نهائية
st.success("نتمنى لك رحلة آمنة!")
