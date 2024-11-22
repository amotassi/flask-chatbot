from flask import Flask, request, jsonify
import google.generativeai as ai
import re

# Initialisation de Flask
app = Flask(__name__)

# Clé API
API_KEY = 'AIzaSyANjEosVPe5kW5YmQX274353Zd0VGo1ZvY'

# Configuration de l'API
ai.configure(api_key=API_KEY)

# Création d'un modèle et démarrage de la conversation
model = ai.GenerativeModel('gemini-pro')
chat = model.start_chat()


def generate_image_description(location):
    return f"Image of {location}. This might include landmarks, popular restaurants, or cultural spots."


def make_links_clickable(text):
    """
    Détecte les URL dans le texte et les transforme en liens HTML.
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

            # Ajouter des images
            image_description = generate_image_description(location)
            bot_response += f"\n\n{image_description}"

        # Convertir les URL dans la réponse en liens HTML cliquables
        bot_response = make_links_clickable(bot_response)

        # Retour de la réponse du bot
        return jsonify({'response': bot_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Point de départ du serveur
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
