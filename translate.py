from flask import Flask, render_template, request
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

# Demo text
demo_text = "Welcome to the Flask Translation App. Select a language to translate this text."

# Language options
languages = {
    "en": "English",
    "ja": "Japanese",
    "es": "Spanish",
    "de": "German",
    "fr": "French",
    "ko": "Korean",
    "hi": "Hindi"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = demo_text  # Default text
    selected_language = "en"    # Default language

    if request.method == 'POST':
        selected_language = request.form.get('language')
        translated_text = translator.translate(demo_text, src='en', dest=selected_language).text

    return render_template('translate.html', demo_text=demo_text, languages=languages, translated_text=translated_text, selected_language=selected_language)

if __name__ == '__main__':
    app.run(debug=True)
