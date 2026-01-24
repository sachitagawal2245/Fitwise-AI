FitWise AI 🏋️‍♂️
An AI-Powered Personalized Fitness & Diet Planner for Students
FitWise AI is a web-based application that generates personalized fitness and diet plans for students using Artificial Intelligence. The system takes user-specific inputs such as physical attributes, fitness goals, activity level, available time, equipment, and dietary preferences, and provides customized recommendations.

 Features:
1 .Personalized workout plan
2 .Personalized diet plan
3 .AI-based recommendations
4 .Simple and interactive user interface
5 .Plan regeneration feature
6 .Secure API key handling using environment variables

 Tech Stack
Programming Language: Python
Frontend / UI: Streamlit
AI Model / API: OpenRouter (LLM API)
Libraries:streamlit,requests,python-dotenv

 How It Works
1. User enters personal fitness details.
2 .The system validates the input.
3 .A structured prompt is generated.
4 .The prompt is sent to an AI model.
5 .The AI generates:Workout plan , Diet plan,Explanation
6 Results are displayed on the web interface.

 How to Run the Project
1. Clone the repository
git clone https://github.com/yourusername/fitwise-ai.git
cd fitwise-ai
2. Install dependencies
pip install -r requirements.txt
3. Create .env file
Create a file named .env in the project folder:
OPENROUTER_API_KEY=your_api_key_here
4. Run the application
streamlit run app.py
 Environment Variables
The project uses environment variables for security.
The .env file is ignored using .gitignore.
For deployment (Streamlit Cloud), add the key in Secrets:
OPENROUTER_API_KEY="your_api_key_here"

 Output
The system generates:
Weekly workout plan
Daily diet plan
Short explanation of the recommendations
All results are displayed in a structured and user-friendly format.

 Future Scope
Integration with wearable devices
Calorie tracking and progress monitoring
Mobile app version
Multilingual support
Medical-condition-aware recommendations
Cloud deployment

 Author

Sachit Agarwal
