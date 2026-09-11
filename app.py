from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    import os
    os.system("python -m spacy download es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

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
    cv_doc = nlp(cv_text.lower())
    plaza_doc = nlp((plaza_titulo + ' ' + plaza_desc).lower())
    
    cv_keywords = set()
    plaza_keywords = set()
    
    for token in cv_doc:
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']:
            cv_keywords.add(token.text)
    
    for token in plaza_doc:
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']:
            plaza_keywords.add(token.text)
    
    if len(plaza_keywords) == 0:
        return 20
    
    matches = len(cv_keywords.intersection(plaza_keywords))
    coverage = matches / len(plaza_keywords)
    score = 30 + (coverage * 50)
    
    if any(word in cv_text.lower() for word in ['años', 'years', 'experiencia']):
        score += 10
    
    if any(word in cv_text.lower() for word in ['licenciatura', 'degree', 'carrera', 'técnico']):
        score += 10
    
    return min(100, max(20, score))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
