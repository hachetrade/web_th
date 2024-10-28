from functools import reduce
from flask import Flask, request, render_template, send_file
import os, pdfplumber
import re
import json
import math
import pandas as pd



app = Flask(__name__)

def upload_and_process_cmo(lines):

    units = getattr(cmo_pdf_label, 'units', None)
    if pdf_path and units:
        output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if output_path:
            convert_cmo_to_excel(pdf_path, output_path, units)
            messagebox.showinfo("Success", f"CMO lista de componentes procesado y guardado en {output_path}")
            cmo_excel_label.config(text=os.path.basename(output_path))

def convert_cmo_to_excel(lines,selection):
    headers = ['#', 'Cantidad', 'Referencia', 'Precio unitario', 'Proveedor']
    all_lines_match = []
    pattern_01 = r'^(\d{3}) (\d+)'
    pattern_03 = r'^\d{3} \d+ (.+?) S'
    pattern_04 = r'(\d{1,3}(?:,\d{2}))'

    for line in lines:
        matches = re.match(pattern_01, line)
        if matches:
            ref = matches.group(1)
            Proveedor = selection['proveedor']
            cantidad_pdf = int(matches.group(2))
            match_articulo = re.search(pattern_03, line)
            match_precio = re.search(pattern_04, line)
            if match_articulo and match_precio:
                articulo = match_articulo.group(1)
                precio = float((match_precio.group(1).replace(',', '.')))
                all_lines_match.append([ref, cantidad_pdf, articulo, precio, Proveedor])

    df = pd.DataFrame(all_lines_match, columns=headers)
    quantities = df['cantidad_pdf']
    mcd = calcular_mcd(quantities)
    df['cantidad'] = df['cantidad_pdf'] / mcd
    df.to_excel(output_path, index=None)


def calcular_mcd(list):
    return reduce(math.gcd, list)
def extract_lines(filepath):
    lines_list = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')
            for line in lines:
                lines_list.append(line)
        return lines_list

def select_type(lines):
    matched_type = {}
    vendors = {
        'proveedor': ['CORTES METALÚRGICOS OVIEDO, S.L.', 'EBAKILAN TOLOSA S.L.'],
        'tipo': ['presupuesto', 'albarán', 'bom']
    }
    for key, value in vendors.items():
        for line in lines:
            for el in value:
                # print(f'elemento a checkear {el}', f'linea : {line}')
                if el.lower() in line.lower():
                    matched_type[key] = el
                    # if matched_type['tipo'] and matched_type['tipo'] == 'bom':
                    #
                    #      break
    matched_type['proveedor'] = vendors['proveedor'][0] if matched_type['tipo'] == 'bom' else matched_type['proveedor']
    return matched_type


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Ningún archivo seleccionado"
    file = request.files['file']
    print(file)
    filename = file.filename
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    lines = extract_lines(filepath)
    for line in lines:
        print(line)
    selection = select_type(lines)
    # render_template('display_lines.html', lines=lines, selection=selection)
    # match selection:
    #     case {'proveedor': 'CORTES METALÚRGICOS OVIEDO, S.L.', 'tipo': 'albarán'}:
    #
    #     case {'proveedor': 'CORTES METALÚRGICOS OVIEDO, S.L.', 'tipo': 'presupuesto'}:
    #          # funcion extraccion de datos y creacion de excel
    #     case {'proveedor': 'CORTES METALÚRGICOS OVIEDO, S.L.', 'tipo': 'bom'}:
    #          # funcion extraccion de datos y creacion de excel
    #     case {'proveedor': 'EBAKILAN TOLOSA S.L.'}:
    #          # funcion extraccion de datos y creacion de excel

    return render_template('display_lines.html', lines=lines, selection=selection)

if __name__ == '__main__':
    app.run()
