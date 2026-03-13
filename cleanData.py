from pathlib import Path
import pandas as pd

thispath = Path(__file__).parent


if __name__ == "__main__":
    from updateJson import ReparadorDivisionPanama

    ruta_base = Path(__file__).parent
    archivo_json = ruta_base / "panamaDivision.json"
    archivo_salida = ruta_base / "test.json"

    # Importamos csv
    with open("censo2023.csv", "r", encoding="utf-8") as f:
        datos_censo = f.read()

    try:
        reparador = ReparadorDivisionPanama(archivo_json, pathname=ruta_base)

        # Ejecutamos la inyección masiva
        reparador.actualizar_desde_csv_jerarquico(datos_censo)

        # Guardamos el JSON actualizado
        reparador.guardar(archivo_salida)

    except FileNotFoundError as e:
        print(f"Error: {e}")
