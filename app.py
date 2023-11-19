from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = 'justpullthetrigger'  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo foi enviado')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)

        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in ['xlsx', 'csv']:
            flash('Formato de arquivo não suportado, aceito somente .xlsx e .csv')
            return redirect(url_for('index'))

        try:
            if file_ext == 'xlsx':
                df = pd.read_excel(file)
            elif file_ext == 'csv':
                df = pd.read_csv(file)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file, encoding='iso-8859-1')
            except Exception as e:
                flash('Erro ao ler o arquivo CSV: somente tipos iso-8859-1 ou UTF-8, converta para xlxs')
                return redirect(url_for('index'))

        registros_por_aba = int(request.form['registros_por_aba'])

        total_registros = len(df)
        numero_abas = total_registros // registros_por_aba + (total_registros % registros_por_aba > 0)

        abas = [df[i:i+registros_por_aba] for i in range(0, total_registros, registros_por_aba)]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for i, aba in enumerate(abas):
                aba.to_excel(writer, sheet_name=f'Aba {i+1}', index=False)

        output.seek(0)

        return send_file(
            output, 
            download_name="base_dados_dividida.xlsx", 
            as_attachment=True
        )

if __name__ == '__main__':
    app.run(debug=True)
