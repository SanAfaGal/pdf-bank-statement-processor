import os
import re
from datetime import datetime

import PyPDF2
import pdfplumber
from dotenv import load_dotenv
import locale

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


def desencriptar_pdf(pdf_path, password):
    """Desencripta un archivo PDF si está encriptado."""
    try:
        with open(pdf_path, 'rb') as archivo_pdf:
            lector_pdf = PyPDF2.PdfReader(archivo_pdf)

            if lector_pdf.is_encrypted:
                lector_pdf.decrypt(password)
                print("Archivo desencriptado exitosamente.")
            else:
                print("El archivo no está encriptado.")
                return

            # Crear un nuevo archivo PDF desencriptado
            escritor_pdf = PyPDF2.PdfWriter()
            for pagina in range(len(lector_pdf.pages)):
                escritor_pdf.add_page(lector_pdf.pages[pagina])

            with open(pdf_path, 'wb') as archivo_salida:
                escritor_pdf.write(archivo_salida)

    except Exception as e:
        print(f"Error al desencriptar el PDF: {e}")


def obtener_iniciales(nombre_completo):
    """Extrae las iniciales del nombre completo."""
    return ''.join(nombre[0].upper() for nombre in nombre_completo.split())


def extraer_datos_nequi(ruta_pdf):
    """Extrae datos del archivo PDF para NEQUI."""
    with pdfplumber.open(ruta_pdf) as pdf:
        primera_pagina = pdf.pages[0]
        texto_completo = primera_pagina.extract_text()

        # Extraer las iniciales del nombre completo
        patron_nombre = re.search(r'(?<=de:)\s*([^\n\r]+)', texto_completo)
        nombre_completo = patron_nombre.group(1).strip() if patron_nombre else ""
        iniciales = obtener_iniciales(nombre_completo)

        # Extraer el periodo de facturación
        patron_periodo = re.search(r'(\d{4}/\d{2}/\d{2})\s*a\s*(\d{4}/\d{2}/\d{2})', texto_completo)
        fecha = patron_periodo.group(1) if patron_periodo else None
        fecha = datetime.strptime(fecha, '%Y/%m/%d')

        # Extraer el total de abonos y cargos
        total_abonos = extraer_total(texto_completo, 'Total abonos')
        total_cargos = extraer_total(texto_completo, 'Total cargos')

        return iniciales, fecha, total_abonos, total_cargos


def extraer_datos_daviplata(ruta_pdf):
    """Extrae datos del archivo PDF para DAVIPLATA."""
    with pdfplumber.open(ruta_pdf) as pdf:
        primera_pagina = pdf.pages[0]
        texto_completo = primera_pagina.extract_text()

        patron_nombre = re.search(r'(?<=cliente:)\s*(.+)\s*(?=Informe)', texto_completo)
        nombre_completo = patron_nombre.group(1).strip() if patron_nombre else ""
        iniciales = obtener_iniciales(nombre_completo)

        patron_periodo = re.search(r'Informe del mes:\s*(\w+)\s*/\s*(\d{4})', texto_completo)
        mes, ano = patron_periodo.groups() if patron_periodo else (None, None)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        fecha = datetime.strptime(f'{ano}/{mes}/01', '%Y/%B/%d')

        total_abonos = extraer_total(texto_completo, 'Más créditos')
        total_cargos = extraer_total(texto_completo, 'Menos débitos')

        return iniciales, fecha, total_abonos, total_cargos


def extraer_total(texto, etiqueta):
    """Extrae el total de abonos o cargos del texto."""
    patron = re.search(fr'{etiqueta}\s*\$*([\d,.]+)', texto)
    return patron.group(1).replace(',', '').replace('.', ',') if patron else '0'


def generar_nombre_archivo(banco, iniciales, fecha):
    """Genera un nuevo nombre de archivo basado en la información extraída."""
    return f"{banco}_{iniciales}_{fecha.year}_{fecha.month:02}.pdf"


def procesar_pdf(banco, ruta_pdf):
    """Procesa un archivo PDF y devuelve el nuevo nombre y totales."""
    if banco == 'NEQUI':
        return extraer_datos_nequi(ruta_pdf)
    elif banco == 'DAVIPLATA':
        return extraer_datos_daviplata(ruta_pdf)
    # Agregar más elif para otros bancos
    else:
        print("Banco no soportado.")
        return None


def procesar_pdfs_en_carpeta(banco, carpeta, password=None):
    """Procesa todos los archivos PDF en una carpeta."""
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.pdf'):
            ruta_pdf = os.path.join(carpeta, archivo)
            desencriptar_pdf(ruta_pdf, password)
            resultado = procesar_pdf(banco, ruta_pdf)
            if resultado:
                iniciales, fecha_fin, total_abonos, total_cargos = resultado
                nuevo_nombre = generar_nombre_archivo(banco, iniciales, fecha_fin)
                nueva_ruta = os.path.join(carpeta, nuevo_nombre)
                os.rename(ruta_pdf, nueva_ruta)
                print(f"Archivo renombrado a: {nuevo_nombre}")
                print(f"Total Abonos: {total_abonos}")
                print(f"Total Cargos: {total_cargos}")
                # print(total_abonos)
                # print(total_cargos)


def main():
    bancos = {1: 'NEQUI', 2: 'DAVIPLATA'}
    print(bancos)
    opcion = int(input('Seleccione el nombre del banco: '))
    banco_seleccionado = bancos.get(opcion)

    # Obtener la carpeta y la contraseña de las variables de entorno
    carpeta_pdfs = os.getenv('PDF_FOLDER')
    password = os.getenv('PDF_PASSWORD')

    if carpeta_pdfs and password:
        procesar_pdfs_en_carpeta(banco_seleccionado, carpeta_pdfs, password)
    else:
        print("Las variables de entorno no están configuradas correctamente.")


if __name__ == "__main__":
    main()
