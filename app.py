import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    sw = int(data['sheetW'])
    sh = int(data['sheetH'])
    kerf = int(data['kerf']) 
    raw_parts = data['parts']
    
    parts = []
    for p in raw_parts:
        for _ in range(int(p['qty'])):
            parts.append({'w': int(p['w']), 'h': int(p['h'])})
            
    # Sort parts by area (descending)
    parts.sort(key=lambda x: x['w'] * x['h'], reverse=True)
    sheets = []

    def find_space(sheet, pw, ph):
        step = 15 # Grid step in mm
        required_w = pw + kerf
        required_h = ph + kerf
        
        for y in range(0, sh - ph + 1, step):
            for x in range(0, sw - pw + 1, step):
                overlap = False
                for p in sheet['placed']:
                    if not (x + required_w <= p['x'] or x >= p['x'] + p['w'] + kerf or 
                            y + required_h <= p['y'] or y >= p['y'] + p['h'] + kerf):
                        overlap = True
                        break
                if not overlap:
                    return x, y
        return None

    for part in parts:
        # Check if part fits in either normal or rotated orientation
        can_fit_normal = part['w'] <= sw and part['h'] <= sh
        can_fit_rotated = part['h'] <= sw and part['w'] <= sh
        
        if not can_fit_normal and not can_fit_rotated:
            return jsonify({'error': f"Part {part['w']}x{part['h']} physically exceeds sheet bounds!"}), 400
            
        placed = False
        for sheet in sheets:
            # 1. Try to place in original orientation
            if can_fit_normal:
                space = find_space(sheet, part['w'], part['h'])
                if space:
                    x, y = space
                    sheet['placed'].append({'w': part['w'], 'h': part['h'], 'x': x, 'y': y})
                    placed = True
                    break
            
            # 2. If it doesn't fit, try rotating 90 degrees
            if can_fit_rotated:
                space = find_space(sheet, part['h'], part['w'])
                if space:
                    x, y = space
                    sheet['placed'].append({'w': part['h'], 'h': part['w'], 'x': x, 'y': y})
                    placed = True
                    break
                
        if not placed:
            new_sheet = {'placed': []}
            # Choose best starting orientation for the brand new sheet
            if can_fit_normal:
                new_sheet['placed'].append({'w': part['w'], 'h': part['h'], 'x': 0, 'y': 0})
            else:
                new_sheet['placed'].append({'w': part['h'], 'h': part['w'], 'x': 0, 'y': 0})
            sheets.append(new_sheet)

    return jsonify({'sheets': sheets})

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
