import csv


class Page:
    def __init__(self, number, R=0, M=0):
        self.number = number
        self.R = R
        self.M = M

    def class_nru(self):
        return 2 * self.R + self.M  # Clase 0 a 3

    def __str__(self):
        return f"{self.number} R={self.R} M={self.M}"

def snapshot_memory(memory):
    return [str(p) if p else "-" for p in memory]

def reset_R_bits(memory):
    """Resetea los bits R de todas las páginas en memoria (simula timer)."""
    for page in memory:
        if page is not None:
            page.R = 0

def nru_simulation(ref_stream, frames_count, reset_interval=4):
    memory = [None] * frames_count  # marcos fijos
    fallos = 0
    ref_counter = 0
    

    print("\nReferencia |", end=" ")
    for i in range(frames_count):
        print(f"Marco {i+1}".ljust(12), end=" | ")
    print("Fallo | Reset_R")
    print("-" * (13 + frames_count * 15 + 18))

    marcos_output = [[] for _ in range(frames_count)]
    fallo_row = []

    for ref in ref_stream:
        page_number, op = ref.split('-')
        page_number = int(page_number)
        op = op.upper()

        ref_counter += 1

        # Reset periódico ANTES de procesar la referencia actual
        reset_occurred = False
        if (ref_counter - 1) % reset_interval == 0 and ref_counter != 1:
            reset_R_bits(memory)
            reset_occurred = True

        # Buscar si la página está en memoria
        in_memory = False
        for page in memory:
            if page is not None and page.number == page_number:
                page.R = 1
                if op == 'W':
                    page.M = 1
                in_memory = True
                break

        fallo = False
        if not in_memory:
            fallos += 1
            fallo = True
            try:
                empty_index = memory.index(None)
            except ValueError:
                empty_index = None

            if empty_index is not None:
                memory[empty_index] = Page(page_number, R=1, M=(1 if op == 'W' else 0))
            else:
                # Algoritmo NRU estándar: buscar víctima por clase
                classes = {0: [], 1: [], 2: [], 3: []}
                for i, page in enumerate(memory):
                    if page is not None:
                        classes[page.class_nru()].append(i)
                
                # Seleccionar víctima de la clase más baja disponible
                victim_index = None
                for cls in range(4):
                    if classes[cls]:
                        victim_index = classes[cls][0]  # Primer índice, no último
                        break
                
                if victim_index is not None:
                    new_M = 1 if op == 'W' else 0
                    memory[victim_index] = Page(page_number, R=1, M=new_M)

        # Imprimir y guardar snapshot
        snapshot = snapshot_memory(memory)
        print(f"{ref:>9} |", end=" ")
        for marco_str in snapshot:
            print(marco_str.ljust(12), end=" | ")
        print(f"{'F' if fallo else ' ':>5} | {'R' if reset_occurred else ' ':>7}")
        for i in range(frames_count):
            marcos_output[i].append(snapshot[i])
        fallo_row.append("F" if fallo else "X")

    # Encabezado CSV y resumen
    final_csv_rows = []
    final_csv_rows.append(["Numero de fallos", str(fallos)] + ["" for _ in range(len(ref_stream)-1)])
    final_csv_rows.append(["Rendimiento", f"{int(100 * (len(ref_stream) - fallos) / len(ref_stream))}%"] + ["" for _ in range(len(ref_stream)-1)])
    final_csv_rows.append([""] + [r for r in ref_stream])
    for i in range(frames_count):
        final_csv_rows.append([f"Marco{i+1}"] + marcos_output[i])
    final_csv_rows.append(["FALLO"] + fallo_row)

    with open("nru_simulacion.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(final_csv_rows)

    tasa_fallos = fallos / len(ref_stream)
    rendimiento = 100 * (len(ref_stream) - fallos) / len(ref_stream)
    return fallos, tasa_fallos, rendimiento

# Datos del ejemplo
referencias = [
    "2-R", "2-W", "3-R", "1-R", "1-W",
    "3-R", "4-W", "5-R", "1-R", "1-W",
    "2-R", "3-W", "4-R"
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

print("\n=== CAMBIOS REALIZADOS ===")
print("1. Reset ANTES de procesar referencias 5, 9, 13, etc.")
print("2. Selección de víctima: primer índice de clase más baja")
print("3. Eliminada regla especial para página 1 en Marco 1")
print("4. Mejora visual: '-' para marcos vacíos")