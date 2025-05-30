from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai

cuisines = [
    "Italian", "Mexican", "Chinese", "Indian", "Japanese", "Thai", "French", "Mediterranean", "American","Greek"
]
languages = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Russian': 'ru',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Arabic': 'ar',
    'Dutch': 'nl',
    'Swedish': 'sv',
    'Turkish': 'tr',
    'Greek': 'el',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Indonesian': 'id',
    'Thai': 'th',
    'Filipino': 'tl',
    'Vietnamese': 'vi',
}
dietary_restrictions = [
    "Gluten-Free",
    "Dairy-Free",
    "Vegan",
    "Pescatarian",
    "Nut-Free",
    "Kosher",
    "Halal",
    "Low-Carb",
    "Organic",
    "Locally Sourced",
]
# Flask 앱 초기화
app = Flask(__name__)

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Google Gemini API 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemma-3n-e4b-it')

@app.route('/')
def index():
    return render_template('index.html', cuisines=cuisines, dietary_restrictions=dietary_restrictions, languages=languages)

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    # 사용자 입력 받기
    ingredients = request.form.getlist('ingredient')

    selected_cuisine = request.form.get('cuisine')
    selected_restrictions = request.form.getlist('restrictions')
    selected_language = request.form.get('language')

    if len(ingredients) != 3:
        return "Kindly provide exactly 3 ingredients."

    # Craft a conversational prompt for ChatGPT, specifying our needs
    prompt = f"Craft a recipe in HTML in {selected_language} using " \
         "{', '.join(ingredients)}. It's okay to use some other necessary " \
         "ingredients. Ensure the recipe ingredients appear at the top, " \
         "followed by the step-by-step instructions."
    if selected_cuisine:
        prompt += f" The cuisine should be {selected_cuisine}."
    if selected_restrictions and len(selected_restrictions) > 0:
        prompt += f" The recipe should have the following restrictions: {', '.join(selected_restrictions)}."
    # Gemini API 호출
    try:
        response = model.generate_content(prompt)
        recipe = response.text # Gemini 응답에서 텍스트 추출

        if recipe.startswith('```html'):
            recipe = recipe.replace('```html', '', 1)
        if recipe.endswith('```'):
            recipe = recipe.rsplit('```', 1)[0]
        recipe = recipe.strip()

        english_explanation_marker = "Key improvements and explanations:"
        if english_explanation_marker in recipe:
            recipe = recipe.split(english_explanation_marker, 1)[0].strip()

    except Exception as e:
        recipe = f"Error generating recipe: {str(e)}"

    return render_template('recipe.html', recipe=recipe)

if __name__ == '__main__':
    app.run(debug=True)