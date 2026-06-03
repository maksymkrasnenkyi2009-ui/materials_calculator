import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        # Зчитуємо дані з форми
        sheet_width = float(request.form.get('sheet_width', 2440))
        sheet_height = float(request.form.get('sheet_height', 1220))
        blade_kerf = float(request.form.get('blade_kerf', 4))
        
        widths = request.form.getlist('part_width[]')
        heights = request.form.getlist('part_height[]')
        qtys = request.form.getlist('part_qty[]')
        
        # Перетворюємо у числа
        parts = []
        for i in range(len(widths)):
            if widths[i] and heights[i] and qtys[i]:
                parts.append({
                    'width': float(widths[i]),
                    'height': float(heights[i]),
                    'qty': int(qtys[i])
                })
        
        # Твоя логіка розрахунку (поки повертаємо статус успіху для тесту)
        return f"<h3>Data Received Successfully!</h3><p>Main sheet: {sheet_width}x{sheet_height}</p><p>Parts count: {len(parts)}</p><br><a href='/'>Go Back</a>"
    
    except Exception as e:
        return f"Error: {str(e)}", 400

if __name__ == '__main__':
    # Обов'язкові налаштування порту для Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
