from datetime import datetime
import pytz

# Configurar zona horaria de Argentina
tz = pytz.timezone('America/Argentina/Buenos_Aires')
fecha_hora_actual = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Prueba de Concepto - Mundial</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
        .container {{ background: white; padding: 30px; display: inline-block; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        p {{ font-size: 1.2em; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Última actualización</h1>
        <p><strong>Fecha y Hora:</strong> {fecha_hora_actual} (ARG)</p>
    </div>
</body>
</html>
"""

with open("mundial.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML generado con éxito.")
