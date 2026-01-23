import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")### Enter your Api key
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "ai_output" not in st.session_state:
    st.session_state.ai_output = None
# ---------------- Page Config ----------------
st.set_page_config(page_title="FITWISE AI",layout="centered")
st.title("💪 FitWise AI")
st.subheader("AI-powered  Fitness & Diet Planner")
st.info("This tool provides general fitness and diet guidance based on preferences and available time. "
    "It is not a substitute for medical advice."
)
# ---------------- Form ----------------
with st.form("fitness"):
    st.markdown("###  Enter your details")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, step=1)
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=200.0, step=0.5)
    country = st.text_input("Country")
    goal = st.selectbox("Fitness Goal",["Fat loss", "Weight gain", "General fitness"])
    gender = st.selectbox("Gender (optional)",["Prefer not to say", "Male", "Female"])
    daily_time = st.number_input("Available Time per Day (minutes)",min_value=10,max_value=180,step=5)
    target_weight = st.number_input("Target Weight (kg)",min_value=10,max_value=200,step=1)
    equipments = st.selectbox("Equipment Available",[ "None","Basic (Dumbbell / Resistance Band)","Medium (Gym Machines)","High (Fully Equipped Gym)" ])
    diet_preference = st.selectbox("Diet Preference",["Veg", "Non-veg", "Both"])
    activity_level = st.selectbox("Activity Level",["Sedentary", "Lightly active", "Moderately active"])
    submit_btn = st.form_submit_button("Generate My Plan")
def derive_workout_intensity(daily_time, activity_level):
    if daily_time < 20:
        base = "short and light"
    elif daily_time <= 45:
        base = "moderate"
    else:
        base = "high intensity"
    if activity_level == "Sedentary":
        return f"{base}, beginner-friendly"
    elif activity_level == "Lightly active":
        return f"{base}, intermediate"
    else:
        return f"{base}, slightly challenging"

def build_prompt(data):
    intensity = derive_workout_intensity(
        data["daily_time"], data["activity_level"]
    )
    prompt = f"""
You are a student fitness assistant.
Generate a personalized fitness and diet plan.
User details:
- Country: {data["country"]}
- Gender: {data["gender"]}
- Age: {data["age"]}
- Height: {data["height"]} cm
- Weight: {data["weight"]} kg
- Goal: {data["goal"]}
- Daily workout time: {data["daily_time"]} minutes
- Activity level: {data["activity_level"]}
- Equipment available: {data["equipment"]}
- Diet preference: {data["diet_preference"]}
Workout rules:
- Workout intensity should be {intensity}
- Avoid unsafe or advanced exercises
- Prefer simple, student-friendly routines
Diet rules:
- Suggest simple, commonly available meals based on country and diet preference
- No supplements
- No medical advice
-for next 7 days
Output format (use EXACT headings):
### WORKOUT PLAN
(Weekly workout plan)
### DIET PLAN
(Daily diet plan)
### EXPLANATION
(Why this plan suits the user)
Keep the language simple and clear.
"""
    return prompt
def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}","Content-Type": "application/json"}
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "system", "content": "You are a helpful fitness assistant."},
            {"role": "user", "content": prompt}],
        "temperature": 0.9
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        raise Exception("AI service failed")
    return response.json()["choices"][0]["message"]["content"]
def split_ai_output(text):
    sections = {"workout": "", "diet": "", "explanation": ""}
    if "### WORKOUT PLAN" in text:
        parts = text.split("### WORKOUT PLAN", 1)[1]
        if "### DIET PLAN" in parts:
            workout, rest = parts.split("### DIET PLAN", 1)
            sections["workout"] = workout.strip()
            if "### EXPLANATION" in rest:
                diet, explanation = rest.split("### EXPLANATION", 1)
                sections["diet"] = diet.strip()
                sections["explanation"] = explanation.strip()
            else:
                sections["diet"] = rest.strip()
    return sections
# ---------------- Validation, AI Call & Output ----------------
if submit_btn:
    errors = []
    required_fields = {
        "Name": name,
        "Country": country
    }
    for field, value in required_fields.items():
        if not value.strip():
            errors.append(f"{field} is required.")
        elif len(value.strip()) < 3:
            errors.append(f"{field} must be at least 3 characters long.")
    if daily_time < 15:
        errors.append("Daily available time should be at least greater then 15 minutes.")
    if goal == "Fat loss" and target_weight >= weight:
        errors.append("For fat loss, target weight should be less then the current weight.")
    if goal == "Weight gain" and target_weight <= weight:
        errors.append("For weight gain, target weight should be greater then  thecurrent weight.")
    if errors:
        for e in errors:
            st.error(e)
    else:
          with st.spinner("Generating your personalized plan..."):
            try:
                st.session_state.user_data = {
                    "name": name,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "goal": goal,
                    "daily_time": daily_time,
                    "activity_level": activity_level,
                    "equipment": equipments,
                    "diet_preference": diet_preference,
                    "country": country,
                    "gender": gender
                }
                st.session_state.ai_output = call_openrouter(
                    build_prompt(st.session_state.user_data)
                )
            except Exception:
                st.error("Failed to generate plan. Please try again.")
    
    
if st.session_state.ai_output:
        sections = split_ai_output(st.session_state.ai_output)
        st.success(f"Plan generated successfully for {st.session_state.user_data['name']} 🚀")
        st.markdown("## 🏋️ Workout Plan")
        st.markdown(sections["workout"] or "Workout plan not available.")
        st.markdown("## 🍽️ Diet Plan")
        st.markdown(sections["diet"] or "Diet plan not available.")
        st.markdown("## 🧠 Why this plan is best  for you")
        st.markdown(sections["explanation"] or "Explanation is not available Sorry for the inconvience caused.")
    # ---------------- Regenerate Button ----------------
if st.session_state.user_data:
    if st.button("🔄 Regenerating your Plan."):
        with st.spinner("Regenerating plan..."):
            try:
                st.session_state.ai_output = call_openrouter(build_prompt(st.session_state.user_data))
                st.rerun()
            except Exception:
                st.error("Failed to regenerate plan. Please try again.")