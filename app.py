import csv

class Page:
    def __init__(self, number, R=0, M=0):
        self.number = number
        self.R = R
        self.M = M

    def class_nru(self):
        return 2 * self.R + self.M  # Clase 0 a 3

def reset_R_bits(memory):
    """Resetea los bits R de todas las páginas en memoria (simula timer)."""
    for page in memory:
        if page is not None:
            page.R = 0

def nru_simulation(ref_stream, frames_count, reset_interval=4):
    memory = [None] * frames_count  # marcos fijos
    fallos = 0
    ref_counter = 0
    
    csv_rows = []
    header = ["Referencia"] + [f"Marco {i+1}" for i in range(frames_count)] + ["Fallo", "Reset_R"]
    csv_rows.append(header)

    print("\nReferencia |", end=" ")
    for i in range(frames_count):
        print(f"Marco {i+1}".ljust(12), end=" | ")
    print("Fallo | Reset_R")
    print("-" * (13 + frames_count * 15 + 18))

    for ref in ref_stream:
        page_number, op = ref.split('-')
        page_number = int(page_number)
        op = op.upper()
        
        ref_counter += 1

        # Reset periódico ANTES de procesar la referencia actual
        # Reset ocurre cada 'reset_interval' referencias, excepto antes de la primera
        reset_occurred = False
        if (ref_counter - 1) % reset_interval == 0 and ref_counter != 1:
            reset_R_bits(memory)
            reset_occurred = True

        # Buscar si la página está en memoria
        in_memory = False
        for page in memory:
            if page is not None and page.number == page_number:
                page.R = 1  # Actualizar bit R
                if op == 'W':
                    page.M = 1  # Actualizar bit M si es escritura
                in_memory = True
                break

        fallo = False
        if not in_memory:
            fallos += 1
            fallo = True

            # Buscar marco vacío
            empty_index = None
            for i in range(frames_count):
                if memory[i] is None:
                    empty_index = i
                    break

            if empty_index is not None:
                # Colocar página en marco vacío
                memory[empty_index] = Page(page_number, R=1, M=(1 if op == 'W' else 0))
            else:
                # Algoritmo NRU puro: seleccionar víctima aleatoria de la clase más baja
                classes = {0: [], 1: [], 2: [], 3: []}
                for i, page in enumerate(memory):
                    if page is not None:
                        classes[page.class_nru()].append(i)
                
                # Buscar la clase más baja con páginas
                victim_index = None
                for cls in range(4):
                    if classes[cls]:
                        victim_index = classes[cls][-1]  # Determinista: última aparición
                        break
                
                # Reemplazar la víctima
                if victim_index is not None:
                    # Si la página a escribir es 'W', M=1, si no, M=0
                    new_M = 1 if op == 'W' else 0
                    memory[victim_index] = Page(page_number, R=1, M=new_M)

        # Imprimir estado de marcos y guardar fila para CSV
        row = [ref]
        print(f"{ref:>9} |", end=" ")
        for i in range(frames_count):
            p = memory[i]
            if p is not None:
                marco_str = f"{p.number} R={p.R} M={p.M}"
                print(marco_str.ljust(12), end=" | ")
                row.append(marco_str)
            else:
                print("-".ljust(12), end=" | ")
                row.append("-")
        print(f"{'F' if fallo else ' ':>5} | {'R' if reset_occurred else ' ':>7}")
        row.append("F" if fallo else "")
        row.append("R" if reset_occurred else "")
        csv_rows.append(row)


    # --- NUEVO FORMATO CSV CON RESUMEN ---
    marcos_output = [[] for _ in range(frames_count)]
    fallo_row = []

    # Recorrer las filas guardadas (excepto el header)
    for row in csv_rows[1:]:
        for i in range(frames_count):
            marco_str = row[i+1] if row[i+1] != "-" else ""
            marcos_output[i].append(marco_str)
        fallo_row.append("F" if row[-2] == "F" else "X")

    # Encabezado CSV y resumen
    final_csv_rows = []
    # Fila de número de fallos
    final_csv_rows.append(["Numero de fallos", str(fallos)] + ["" for _ in range(len(ref_stream)-1)])
    # Fila de rendimiento
    final_csv_rows.append(["Rendimiento", f"{int(100 * (len(ref_stream) - fallos) / len(ref_stream))}%"] + ["" for _ in range(len(ref_stream)-1)])
    # Encabezado de referencias
    final_csv_rows.append([""] + [r for r in ref_stream])
    # Filas de marcos
    for i in range(frames_count):
        final_csv_rows.append([f"Marco{i+1}"] + marcos_output[i])
    # Fila de fallos
    final_csv_rows.append(["FALLO"] + fallo_row)

    # Guarda el nuevo CSV en formato deseado (sobrescribe el anterior)
    with open("nru_simulacion.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(final_csv_rows)

    tasa_fallos = fallos / len(ref_stream)
    rendimiento = 100 * (len(ref_stream) - fallos) / len(ref_stream)
    return fallos, tasa_fallos, rendimiento

# Datos del ejemplo
referencias = [
    "1-R", "1-W", "2-R", "3-R", "4-W",
    "6-R", "3-W", "1-W", "2-W", "4-R"
]




print("=== SIMULACIÓN ALGORITMO NRU ===")
print(f"Referencias: {len(referencias)}")
print(f"Marcos: 4")
print(f"Reset cada: 4 referencias")


fallos, tasa_fallo, rendimiento = nru_simulation(referencias, 4, reset_interval=4)

print(f"\n=== RESULTADOS ===")
print(f"Número de Fallos: {fallos}")
print(f"Tasa de Fallos: {tasa_fallo:.4f}")
print(f"Rendimiento (%): {rendimiento:.2f}%")

print("\n=== CLASES NRU ===")
print("Clase 0: R=0, M=0 (no referenciada recientemente, no modificada)")
print("Clase 1: R=0, M=1 (no referenciada recientemente, modificada)")
print("Clase 2: R=1, M=0 (referenciada recientemente, no modificada)")
print("Clase 3: R=1, M=1 (referenciada recientemente, modificada)")

print(f"\nArchivo CSV guardado: nru_simulacion.csv")

# Demostración manual del comportamiento esperado
print("\n=== ANÁLISIS MANUAL PASO A PASO ===")
print("Referencias 1-4: Sin reset")
print("Referencia 5 (6-R): Reset antes de procesar")
print("Referencia 9 (2-W): Reset antes de procesar")
print("Para 2-W: página 2 debe tener R=1, M=1")
print("Para 4-R: página 4 debe mantener M anterior y R=1")