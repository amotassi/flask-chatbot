from flask import Flask, request, jsonify
import google.generativeai as ai
import re
import os

# Initialisation de Flask
app = Flask(__name__)

# Clé API (vous devez définir la clé API comme une variable d'environnement sur Render)
API_KEY = os.getenv('API_KEY')

# Vérifier si la clé API est disponible
if not API_KEY:
    raise EnvironmentError("La clé API n'est pas définie. Assurez-vous de définir la variable d'environnement 'API_KEY'.")

# Configuration de l'API
ai.configure(api_key=API_KEY)

# Création d'un modèle et démarrage de la conversation
model = ai.GenerativeModel('gemini-pro')
chat = model.start_chat()

def generate_image_description(location):
    return f"Image de {location}. Cela peut inclure des monuments, des restaurants populaires ou des lieux culturels."

def make_links_clickable(text):
    """
    Transforme les URL dans le texte en liens HTML.
    """
    url_pattern = r'(https?://[^\s]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

@app.route('/chat', methods=['POST'])
def chat_with_bot():
    try:
        # Récupération du message de l'utilisateur depuis la requête
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'Message vide.'}), 400

        # Envoi du message au modèle et récupération de la réponse
        response = chat.send_message(user_message)
        bot_response = response.text

        # Détecter si le message de l'utilisateur mentionne un lieu
        if "voyager à" in user_message.lower() or "visiter" in user_message.lower():
            # Extraire le lieu
            location = user_message.split("à")[-1].strip() if "à" in user_message else "destination"

            # Ajouter une description d'image
            image_description = generate_image_description(location)
            bot_response += f"\n\n{image_description}"

        # Convertir les URL dans la réponse en liens HTML cliquables
        bot_response = make_links_clickable(bot_response)

        # Retour de la réponse du bot
        return jsonify({'response': bot_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Démarrage de l'application Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Utilise le port défini par Render, ou 5000 par défaut
    app.run(host='0.0.0.0', port=port)
