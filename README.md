# App de presupuesto — base del proyecto

Réplica en Python de la macro "Totalizar" del Excel original, lista para
conectarse a Google Sheets como almacenamiento (gratis, sincronizado
automáticamente entre cel y PC).

## Archivos
- `config.py` — nombres del spreadsheet, pestañas y columnas.
- `sheets_client.py` — conexión a Google Sheets (leer/escribir como DataFrame).
- `logica.py` — la lógica de negocio (equivalente a `Sub Totalizar()`).
- `app.py` — interfaz Streamlit (resumen, registrar gasto, estado de servicios).

## Paso a paso para conectar a Google Sheets (una sola vez)

1. Entra a [Google Cloud Console](https://console.cloud.google.com/), crea un
   proyecto nuevo (o usa uno existente).
2. Habilita las APIs **Google Sheets API** y **Google Drive API**.
3. Ve a "Credenciales" → "Crear credenciales" → "Cuenta de servicio".
4. Dentro de la cuenta de servicio creada, genera una clave nueva tipo
   **JSON** y descárgala. Renómbrala `credentials.json` y ponla en esta
   carpeta (nunca la subas a un repo público).
5. Copia el correo de la cuenta de servicio (algo como
   `nombre@proyecto.iam.gserviceaccount.com`).
6. Crea un Google Sheet llamado **Presupuesto** (o el nombre que pongas en
   `config.NOMBRE_SPREADSHEET`), con 3 pestañas:
   - `Proyeccion` con encabezados: `Rubro, Proyectado, Gastado, Disponible`
   - `Gastos` con encabezados: `Fecha, Item, Valor, Categoria`
   - `Servicios` con encabezados: `Servicio, Valor`
7. Comparte ese Google Sheet con el correo de la cuenta de servicio (como
   Editor), igual que compartirías un documento con otra persona.

## Cómo correrla en tu PC

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá en tu navegador (`localhost:8501`). Funciona igual en cel y PC porque
es una página web — el siguiente paso es desplegarla en Streamlit Community
Cloud para tener una URL fija accesible desde cualquier dispositivo:

1. Sube esta carpeta a un repositorio de GitHub (**sin** subir `credentials.json`,
   agrégalo a `.gitignore`).
2. Entra a [share.streamlit.io](https://share.streamlit.io), conecta el repo y
   selecciona `app.py` como archivo principal.
3. `sheets_client.py` hoy lee `credentials.json` como archivo local. Para que
   funcione en Streamlit Cloud, ese archivo no puede subirse al repo — cuando
   estemos listos para desplegar, ajustamos `sheets_client.py` para que lea
   las credenciales desde `st.secrets` en vez del archivo (es un cambio
   pequeño, lo hacemos en ese momento).
4. Listo — la misma URL funciona desde el navegador del cel y de la PC.
