from flask import Flask, request, jsonify
from difflib import SequenceMatcher
import re

app = Flask(__name__)

@app.route('/score', methods=['POST'])
def score_cv():
    data = request.json
    cv_text = data.get('cv_text', '')
    plaza_titulo = data.get('plaza_titulo', '')
    plaza_desc = data.get('plaza_descripcion', '')
    
    if not cv_text:
        return jsonify({'error': 'CV text required'}), 400
    
    score = calcular_score(cv_text, plaza_titulo, plaza_desc)
    return jsonify({'score': score})

def calcular_score(cv_text, plaza_titulo, plaza_desc):
    cv_lower = cv_text.lower()
    plaza_full = (plaza_titulo + ' ' + plaza_desc).lower()
    
    # Extraer palabras clave (4+ caracteres)
    cv_words = set(re.findall(r'\b\w{4,}\b', cv_lower))
    plaza_words = set(re.findall(r'\b\w{4,}\b', plaza_full))
    
    if not plaza_words:
        return 20
    
    # Calcular coincidencias
    matches = len(cv_words.intersection(plaza_words))
    coverage = matches / len(plaza_words)
    
    # Score base
    score = 30 + (coverage * 50)
    
    # Bonos
    if any(word in cv_lower for word in ['años', 'years', 'experiencia', 'experience']):
        score += 10
    if any(word in cv_lower for word in ['licenciatura', 'degree', 'carrera', 'técnico', 'bachelor']):
        score += 10
    
    return min(100, max(20, score))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
