import json
import os
from pathlib import Path
import csv
import re
from io import StringIO


class ReparadorDivisionPanama:
    def __init__(self, filename, pathname):
        """Inicializa la clase cargando el JSON de la ruta especificada."""
        self.filepath = pathname
        self.jsonfile = self.filepath / filename

        if not os.path.exists(self.jsonfile):
            raise FileNotFoundError(f"No se encontró el archivo: {self.jsonfile}")

        with open(self.jsonfile, "r", encoding="utf-8") as file:
            self.raw_data = json.load(file)

        if "provincia" in self.raw_data:
            self.provincias = self.raw_data["provincia"]
        else:
            raise ValueError("El JSON no tiene la llave principal 'provincia'.")

    def guardar(self, output_file=None):
        """Guarda los cambios en el archivo. Si no se da una ruta, sobrescribe el original."""
        path = self.jsonfile
        self.raw_data["provincia"] = self.provincias
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.raw_data, file, ensure_ascii=False, indent=2)
        print(f"✅ Cambios guardados en: {path}")

    # --- MÉTODOS DE BÚSQUEDA ---

    def buscar_provincia(self, nombre):
        """Devuelve el diccionario de la provincia si existe."""
        for p in self.provincias:
            if p.get("name", "").upper() == nombre.upper():
                return p
        return None

    def buscar_distrito(self, nombre_distrito, nombre_provincia=None):
        """
        Busca un distrito. Si se le pasa la provincia, busca solo ahí.
        Devuelve una tupla: (diccionario_provincia, diccionario_distrito)
        """
        provincias_a_buscar = (
            [self.buscar_provincia(nombre_provincia)]
            if nombre_provincia
            else self.provincias
        )
        provincias_a_buscar = [p for p in provincias_a_buscar if p is not None]

        for p in provincias_a_buscar:
            for d in p.get("distritos", []):
                if d.get("name", "").upper() == nombre_distrito.upper():
                    return p, d
        return None, None

    # --- MÉTODOS DE REPARACIÓN (CRUD) ---

    def agregar_provincia(self, datos_provincia):
        """Añade una nueva provincia (o comarca) si no existe."""
        if not self.buscar_provincia(datos_provincia.get("name", "")):
            self.provincias.append(datos_provincia)
            print(f"➕ Provincia agregada: {datos_provincia.get('name')}")
        else:
            print(f"⚠️ La provincia {datos_provincia.get('name')} ya existe.")

    def agregar_distrito(self, nombre_provincia, datos_distrito):
        """Añade un distrito a una provincia existente."""
        provincia = self.buscar_provincia(nombre_provincia)
        if provincia:
            _, distrito_existente = self.buscar_distrito(
                datos_distrito.get("name", ""), nombre_provincia
            )
            if not distrito_existente:
                if "distritos" not in provincia:
                    provincia["distritos"] = []
                provincia["distritos"].append(datos_distrito)
                print(
                    f"➕ Distrito agregado: {datos_distrito.get('name')} en {nombre_provincia}"
                )
            else:
                print(
                    f"⚠️ El distrito {datos_distrito.get('name')} ya existe en {nombre_provincia}."
                )
        else:
            print(f"❌ Error: No se encontró la provincia {nombre_provincia}.")

    def agregar_corregimiento(self, nombre_distrito, datos_corregimiento):
        """Añade un objeto corregimiento a un distrito específico."""
        _, distrito = self.buscar_distrito(nombre_distrito)

        if distrito:
            if "corregimientos" not in distrito:
                distrito["corregimientos"] = []

            nombre_nuevo = datos_corregimiento.get("name", "").upper()

            # Verificamos si ya existe comparando el 'name'
            existe = False
            for c in distrito["corregimientos"]:
                # Maneja el caso en que el elemento sea un dict o un string (por si hay datos sucios)
                nombre_existente = (
                    c.get("name", "").upper() if isinstance(c, dict) else c.upper()
                )
                if nombre_existente == nombre_nuevo:
                    existe = True
                    break

            if not existe:
                distrito["corregimientos"].append(datos_corregimiento)
                print(
                    f"➕ Corregimiento '{nombre_nuevo}' agregado a {nombre_distrito}."
                )
            else:
                print(
                    f"⚠️ El corregimiento '{nombre_nuevo}' ya existe en {nombre_distrito}."
                )
        else:
            print(f"❌ Error: No se encontró el distrito {nombre_distrito}.")

    def remover_corregimiento(self, nombre_distrito, nombre_corregimiento):
        """Elimina un corregimiento de un distrito."""
        _, distrito = self.buscar_distrito(nombre_distrito)
        if distrito and "corregimientos" in distrito:
            lista_original = len(distrito["corregimientos"])
            distrito["corregimientos"] = [
                c
                for c in distrito["corregimientos"]
                if (
                    c.get("name", "").upper() != nombre_corregimiento.upper()
                    if isinstance(c, dict)
                    else c.upper() != nombre_corregimiento.upper()
                )
            ]
            if len(distrito["corregimientos"]) < lista_original:
                print(
                    f"➖ Corregimiento {nombre_corregimiento.upper()} removido de {nombre_distrito}."
                )

    def mover_corregimiento(
        self, origen_distrito, destino_distrito, nombre_corregimiento
    ):
        """Saca un corregimiento de un distrito y lo mete en otro."""
        print(
            f"🔄 Moviendo {nombre_corregimiento} de {origen_distrito} a {destino_distrito}..."
        )
        self.remover_corregimiento(origen_distrito, nombre_corregimiento)
        self.agregar_corregimiento(destino_distrito, nombre_corregimiento)

    def limpiar_nombre_inec(self, nombre):
        """Elimina notas entre paréntesis como '(4)' o '(cabecera)' y espacios extra."""
        nombre_limpio = re.sub(r"\(.*?\)", "", nombre)
        return nombre_limpio.strip()

    def actualizar_desde_csv_jerarquico(self, texto_csv):
        """
        Procesa el CSV exportado del INEC con formato jerárquico
        (Provincia en col 0, Distrito en col 1, Corregimiento en col 2)
        """
        print("📊 Procesando datos del Censo 2023...")

        # Leemos el texto CSV usando la librería nativa para respetar las comillas en los números
        lector = csv.reader(StringIO(texto_csv.strip()))
        next(lector)  # Saltamos la cabecera (Provincia,,,Superficie23...)

        provincia_actual = None
        distrito_actual = None

        for fila in lector:
            # Si la fila está vacía, saltamos
            if not any(fila):
                continue

            col_prov = fila[0].strip() if len(fila) > 0 else ""
            col_dist = fila[1].strip() if len(fila) > 1 else ""
            col_corr = fila[2].strip() if len(fila) > 2 else ""

            # Extraemos los valores limpiando las comas de los miles (ej. "101,091" -> "101091")
            sup23 = fila[3].replace(",", "").strip() if len(fila) > 3 else ""
            pob23 = fila[4].replace(",", "").strip() if len(fila) > 4 else ""
            den23 = fila[5].replace(",", "").strip() if len(fila) > 5 else ""

            # Detectar en qué nivel estamos
            if col_prov and col_prov != "TOTAL":
                provincia_actual = self.limpiar_nombre_inec(col_prov)

            elif not col_prov and col_dist:
                distrito_actual = self.limpiar_nombre_inec(col_dist)

            elif not col_prov and not col_dist and col_corr:
                corregimiento_actual = self.limpiar_nombre_inec(col_corr)

                # Buscamos el distrito en nuestro JSON
                _, distrito = self.buscar_distrito(distrito_actual, provincia_actual)

                if distrito and "corregimientos" in distrito:
                    encontrado = False
                    for c in distrito["corregimientos"]:
                        nombre_json = (
                            c.get("name", "").upper()
                            if isinstance(c, dict)
                            else c.upper()
                        )

                        # Si el nombre coincide
                        if nombre_json == corregimiento_actual.upper():
                            encontrado = True
                            print(c)
                            if isinstance(c, dict):
                                c["superficie23"] = sup23
                                c["pop23"] = pob23
                                c["den23"] = den23
                            break

                    if encontrado:
                        print(
                            f"✅ {corregimiento_actual} ({distrito_actual}) actualizado -> Pob: {pob23}"
                        )
                    else:
                        print(
                            f"⚠️ No se encontró el corregimiento: {corregimiento_actual} en {distrito_actual}"
                        )


# ==========================================
if __name__ == "__main__":
    # json en la misma dirección
    archivo_json = "panamaDivision.json"
    pathname = Path(__file__).parent
    # Instanciamos nuestra herramienta
    reparador = ReparadorDivisionPanama(archivo_json, pathname)

    # Buscar algo para ver si existe
    prov = reparador.buscar_provincia("CHIRIQUÍ")
    if prov:
        print(
            f"🔍 Chiriquí encontrado. Tiene {len(prov.get('distritos', []))} distritos."
        )

    nuevo_corregimiento = {
        "provincia": "COCLÉ",
        "distrito": "Penonomé",
        "id": "02-6-12",
        "name": "San José de los Cascabeles",
        "superficie": "Pendiente...",
        "pop10": "Pendiente...",
        "den10": "Pendiente...",
    }

    # Agregamos el objeto al distrito de Arraiján
    reparador.agregar_corregimiento(
        nombre_distrito="Penonomé", datos_corregimiento=nuevo_corregimiento
    )

    # # Crear el Distrito de Tierras Altas y mover sus corregimientos desde Bugaba
    # nuevo_distrito = {
    #     "id": "0414",
    #     "name": "TIERRAS ALTAS",
    #     "corregimientos": []
    # }
    # reparador.agregar_distrito("CHIRIQUÍ", nuevo_distrito)

    # corregimientos_a_mover = ["VOLCÁN", "CERRO PUNTA", "CUESTA DE PIEDRA", "NUEVA CALIFORNIA", "PASO ANCHO"]
    # for c in corregimientos_a_mover:
    #     reparador.mover_corregimiento("BUGABA", "TIERRAS ALTAS", c)

    # Guardar los resultados
    reparador.guardar("panamaDivision.json")
