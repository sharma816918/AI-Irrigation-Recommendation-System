import streamlit as st
import json

from ai_helper import (
    extract_irrigation_data,
    generate_irrigation_explanation
)

from fuzzy_logic import get_irrigation_recommendation


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Irrigation System",
    page_icon="🌱",
    layout="centered"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #e8f5e9,
        #f1f8e9,
        #ffffff
    );
}

/* Main title */

.main-title {
    text-align: center;
    color: #1b5e20 !important;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

/* Subtitle */

.subtitle {
    text-align: center;
    color: #4e6e50 !important;
    font-size: 17px;
    margin-bottom: 30px;
}

/* Cards */

.input-card,
.result-card {
    background-color: #ffffff !important;
    color: #222222 !important;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Card text */

.input-card *,
.result-card * {
    color: #222222;
}

/* Section headings */

.section-title {
    color: #2e7d32 !important;
    font-size: 24px;
    font-weight: 700;
}

/* Streamlit metric */

div[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border-radius: 12px;
    padding: 10px;
}

div[data-testid="stMetricLabel"] {
    color: #444444 !important;
}

div[data-testid="stMetricValue"] {
    color: #1b5e20 !important;
    font-weight: 700;
}

/* Text area */

textarea {
    color: #222222 !important;
    background-color: #ffffff !important;
}

/* Text area label */

label {
    color: #222222 !important;
}

/* Normal text */

p {
    color: #222222;
}

/* Footer */

.footer {
    text-align: center;
    color: #607d60 !important;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# TITLE
# ==========================================

st.markdown(
    '<div class="main-title">'
    '🌱 AI Irrigation Recommendation System'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI + LangChain + Fuzzy Logic for Smart Irrigation'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# INPUT SECTION
# ==========================================

st.markdown(
    '<div class="input-card">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">'
    '🌾 Enter Field Conditions'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Describe your crop and field conditions in normal language."
)


# ==========================================
# EXAMPLE
# ==========================================

st.info(
    "💡 Example: My tomato crop has dry soil, "
    "temperature is 34°C, humidity is 45% "
    "and rain chance is 10%."
)


# ==========================================
# INPUT BOX
# ==========================================

user_input = st.text_area(
    "📝 Describe your field",
    height=130,
    placeholder=(
        "Example: My tomato crop has dry soil, "
        "temperature is 34°C, humidity is 45% "
        "and rain chance is 10%."
    )
)


st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# BUTTON
# ==========================================

button = st.button(
    "🌱 Get Irrigation Recommendation",
    type="primary",
    use_container_width=True
)


# ==========================================
# PROCESSING
# ==========================================

if button:

    if not user_input.strip():

        st.warning(
            "⚠️ Please enter your field conditions."
        )

    else:

        try:

            # ==================================
            # AI DATA EXTRACTION
            # ==================================

            with st.spinner(
                "🤖 AI is understanding your field conditions..."
            ):

                extracted_data = extract_irrigation_data(
                    user_input
                )


            # ==================================
            # CONVERT AI RESULT
            # ==================================

            if isinstance(extracted_data, str):

                data = json.loads(
                    extracted_data
                )

            else:

                data = extracted_data


            if isinstance(data, list):

                data = data[0]


            # ==================================
            # GET VALUES
            # ==================================

            crop = data["crop"]

            soil_moisture = float(
                data["soil_moisture"]
            )

            temperature = float(
                data["temperature"]
            )

            humidity = float(
                data["humidity"]
            )

            rain_probability = float(
                data["rain_probability"]
            )


            # ==================================
            # FUZZY LOGIC
            # ==================================

            score, level = get_irrigation_recommendation(

                soil_value=soil_moisture,

                temperature_value=temperature,

                humidity_value=humidity,

                rain_value=rain_probability

            )


            # ==================================
            # SUCCESS MESSAGE
            # ==================================

            st.success(
                "✅ Irrigation recommendation generated!"
            )


            # ==================================
            # AI EXTRACTED INFORMATION
            # ==================================

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-title">'
                '🤖 AI Extracted Information'
                '</div>',
                unsafe_allow_html=True
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "🌾 Crop",
                    crop
                )

                st.metric(
                    "💧 Soil Moisture",
                    f"{soil_moisture}%"
                )

                st.metric(
                    "🌡️ Temperature",
                    f"{temperature}°C"
                )


            with col2:

                st.metric(
                    "💦 Humidity",
                    f"{humidity}%"
                )

                st.metric(
                    "🌧️ Rain Probability",
                    f"{rain_probability}%"
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # ==================================
            # FUZZY RESULT
            # ==================================

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-title">'
                '🧠 Fuzzy Logic Result'
                '</div>',
                unsafe_allow_html=True
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Irrigation Score",
                    f"{score:.2f}"
                )


            with col2:

                st.metric(
                    "Irrigation Level",
                    level
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # ==================================
            # AI EXPLANATION
            # ==================================

            try:

                with st.spinner(
                    "💡 AI is preparing the explanation..."
                ):

                    explanation = (
                        generate_irrigation_explanation(

                            crop=crop,

                            soil_moisture=soil_moisture,

                            temperature=temperature,

                            humidity=humidity,

                            rain_probability=rain_probability,

                            score=score,

                            level=level

                        )
                    )


                st.markdown(
                    '<div class="result-card">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<div class="section-title">'
                    '💡 AI Explanation'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.write(explanation)

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


            except Exception as explanation_error:

                error_text = str(
                    explanation_error
                ).lower()


                if (
                    "429" in error_text
                    or "quota" in error_text
                    or "resource_exhausted" in error_text
                ):

                    st.warning(
                        "⚠️ Gemini API quota is currently "
                        "exhausted. The fuzzy irrigation "
                        "result above is still valid. "
                        "AI explanation will work again "
                        "when Gemini quota becomes available."
                    )

                else:

                    st.warning(
                        "⚠️ AI explanation could not be "
                        "generated right now."
                    )


        except Exception as e:

            error_text = str(e).lower()


            if (
                "429" in error_text
                or "quota" in error_text
                or "resource_exhausted" in error_text
            ):

                st.error(
                    "⚠️ Gemini API quota has been exhausted."
                )

                st.info(
                    "Please wait until the Gemini quota "
                    "resets before testing AI extraction again."
                )

            elif (
                "api key" in error_text
                or "gemini_api_key" in error_text
            ):

                st.error(
                    "❌ Gemini API key is not available."
                )

            else:

                st.error(
                    "❌ Something went wrong."
                )

                st.write(
                    str(e)
                )


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    '<div class="footer">'
    '🌱 AI Irrigation Recommendation System '
    '| LangChain + Gemini + Fuzzy Logic'
    '</div>',
    unsafe_allow_html=True
)