import csv
import json
import re
from pathlib import Path


def limpiar_nombre(nombre):
    """Limpia el texto, quita paréntesis y lo pone en mayúsculas."""
    nombre_limpio = re.sub(r"\(.*?\)", "", nombre)
    return nombre_limpio.strip().upper()


def limpiar_numero(valor):
    """Quita comas y comillas de los números del CSV."""
    return valor.replace(",", "").replace('"', "").strip() if valor else ""


def obtener_columna(fila, indice):
    return fila[indice].strip() if indice < len(fila) else ""


def construir_json_desde_csv(ruta_csv, ruta_salida):
    provincias = []

    provincia_actual = None
    distrito_actual = None

    # CONTADORES PARA LOS IDs JERÁRQUICOS
    contador_provincia = 0
    contador_distrito = 0
    contador_corregimiento = 0

    print(f"📂 Leyendo datos y generando IDs desde {ruta_csv}...")

    try:
        with open(ruta_csv, "r", encoding="utf-8") as f:
            lector = csv.reader(f)

            for fila in lector:
                if not any(fila):
                    continue

                col_prov = obtener_columna(fila, 0)
                col_dist = obtener_columna(fila, 1)
                col_corr = obtener_columna(fila, 2)

                if col_prov.upper() in ["PROVINCIA", "TOTAL"]:
                    continue

                sup23 = limpiar_numero(obtener_columna(fila, 3))
                pob23 = limpiar_numero(obtener_columna(fila, 4))
                den23 = limpiar_numero(obtener_columna(fila, 5))

                # ==========================================
                # 1. NIVEL PROVINCIA / COMARCA
                # ==========================================
                if col_prov:
                    contador_provincia += 1
                    # Formato: "01", "02", "14"
                    id_prov = str(contador_provincia).zfill(2)

                    provincia_actual = {
                        "id": id_prov,
                        "name": limpiar_nombre(col_prov),
                        "superficie23": sup23,
                        "pop23": pob23,
                        "den23": den23,
                        "distritos": [],
                    }
                    provincias.append(provincia_actual)

                    # Al cambiar de provincia, reseteamos el distrito
                    distrito_actual = None
                    contador_distrito = 0

                # ==========================================
                # 2. NIVEL DISTRITO
                # ==========================================
                elif not col_prov and col_dist:
                    if provincia_actual is not None:
                        contador_distrito += 1
                        # Formato: "01-01", "01-02"
                        id_dist = f"{provincia_actual['id']}-{str(contador_distrito).zfill(2)}"

                        distrito_actual = {
                            "id": id_dist,
                            "name": limpiar_nombre(col_dist),
                            "superficie23": sup23,
                            "pop23": pob23,
                            "den23": den23,
                            "corregimientos": [],
                        }
                        provincia_actual["distritos"].append(distrito_actual)

                        # Al cambiar de distrito, reseteamos el corregimiento
                        contador_corregimiento = 0

                # ==========================================
                # 3. NIVEL CORREGIMIENTO
                # ==========================================
                elif not col_prov and not col_dist and col_corr:
                    if distrito_actual is not None:
                        contador_corregimiento += 1
                        # Formato: "01-01-01", "01-01-02"
                        id_corr = f"{distrito_actual['id']}-{str(contador_corregimiento).zfill(2)}"

                        corregimiento_actual = {
                            "id": id_corr,
                            "name": limpiar_nombre(col_corr),
                            "superficie23": sup23,
                            "pop23": pob23,
                            "den23": den23,
                        }
                        distrito_actual["corregimientos"].append(corregimiento_actual)

        datos_finales = {"provincia": provincias}

        with open(ruta_salida, "w", encoding="utf-8") as f_out:
            json.dump(datos_finales, f_out, ensure_ascii=False, indent=2)

        print(
            f"✅ ¡Éxito! JSON creado con {len(provincias)} provincias/comarcas y todos sus IDs jerárquicos."
        )

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{ruta_csv}'.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


# ==========================================
if __name__ == "__main__":
    ruta_base = Path(__file__).parent
    archivo_csv = ruta_base / "censo2023.csv"
    archivo_json = ruta_base / "panama_censo_2023.json"

    construir_json_desde_csv(archivo_csv, archivo_json)
