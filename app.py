from flask import Flask, render_template, request, send_file, url_for
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Se cambio a 500 Mb David Mejia

# Asegúrate de que existe la carpeta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        if 'file' not in request.files:
            return render_template('index.html', error="No se seleccionó ningún archivo")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error="No se seleccionó ningún archivo")
        
        if file and file.filename.endswith('.xlsx'):
            # Guardar el archivo
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Leer el Excel
            df = pd.read_excel(filepath)
            
            # Verificar columnas necesarias
            if 'Nombre' not in df.columns or 'Categoría de producto' not in df.columns:
                return render_template('index.html', error="El archivo debe contener las columnas 'Nombre' y 'Categoría de producto'")
            
            # Buscar duplicados
            duplicados = df[df.duplicated(['Nombre', 'Categoría de producto'], keep=False)]
            
            # Crear reporte
            resultado_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_duplicados.xlsx')
            duplicados.to_excel(resultado_path, index=False)
            
            return render_template('index.html', 
                                 success=f"Análisis completado. Se encontraron {len(duplicados)} productos duplicados",
                                 filename='resultado_duplicados.xlsx')
        
        else:
            return render_template('index.html', error="Por favor sube un archivo Excel (.xlsx)")
    
    except Exception as e:
        return render_template('index.html', error=f"Error procesando el archivo: {str(e)}")

# RUTA FALTANTE - Esta es la que causa el error
@app.route('/descargar/<filename>')
def download_file(filename):
    """Descargar archivo de resultados"""
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        return "Archivo no encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)