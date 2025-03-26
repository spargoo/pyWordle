import json

ARCHIVO_ENTRADA = "diccionario.txt"
ARCHIVO_SALIDA = "palabras5.json"

def obtener_palabras_de_5_letras(entrada):
    palabras_unicas = set()  # set, in order to avoid duplicates
    try:
        with open(entrada, "r", encoding="utf-8") as archivo: # reading
            for linea in archivo:
                palabra = linea.strip().lower()
                # checking only letters and 5 length
                if len(palabra) == 5 and palabra.isalpha():
                    palabras_unicas.add(palabra)
        return list(palabras_unicas)  # converting in list
    except FileNotFoundError:
        print(f"Error: El archivo {entrada} no se encontró.")
        return []

def guardar_en_json(palabras, salida):
    # saving in a json format
    datos = {"palabras": sorted(palabras)}  
    try:
        with open(salida, "w", encoding="utf-8") as archivo: #writing
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        print(f"Se guardaron {len(palabras)} palabras únicas en {salida}")
    except IOError as e:
        print(f"Error al guardar el archivo: {e}")

def main():
    # exe
    palabras = obtener_palabras_de_5_letras(ARCHIVO_ENTRADA)
    if palabras:
        guardar_en_json(palabras, ARCHIVO_SALIDA)
    else:
        print("No se encontraron palabras válidas.")

if __name__ == "__main__":
    main()