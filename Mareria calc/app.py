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
        if part['w'] > sw or part['h'] > sh:
            return jsonify({'error': f"Part {part['w']}x{part['h']} physically exceeds sheet bounds!"}), 400
            
        placed = False
        for sheet in sheets:
            space = find_space(sheet, part['w'], part['h'])
            if space:
                x, y = space
                sheet['placed'].append({'w': part['w'], 'h': part['h'], 'x': x, 'y': y})
                placed = True
                break
                
        if not placed:
            new_sheet = {'placed': []}
            new_sheet['placed'].append({'w': part['w'], 'h': part['h'], 'x': 0, 'y': 0})
            sheets.append(new_sheet)

    return jsonify({'sheets': sheets})

if __name__ == '__main__':
    app.run(debug=True)