import csv


class Page:
    def __init__(self, number, R=0, M=0, timestamp=None):
        self.number = number
        self.R = R
        self.M = M
        self.timestamp = timestamp

    def class_nru(self):
        return 2 * self.R + self.M  # Clase 0 a 3

    def __str__(self):
        return f"{self.number} R={self.R} M={self.M} T={self.timestamp}"


def snapshot_memory(memory):
    return [
        f"{p.number} R={p.R} M={p.M} C={p.class_nru()}" if p else "-"
        for p in memory
    ]


def reset_R_bits(memory):
    """Resetea los bits R solo si ninguna página en memoria tiene M=1. Si hay alguna modificada, no se resetea."""
    # Verificar si alguna página en memoria tiene M=1
    has_modified_pages = any(page.M == 1 for page in memory if page is not None)
    
    if has_modified_pages:
        return False  # No resetear si alguna página está modificada
    
    # Si no hay páginas modificadas, resetear todos los bits R
    for page in memory:
        if page is not None:
            page.R = 0
    
    return True  # Retornar True si se realizó el reset


def nru_simulation(ref_stream, frames_count, reset_interval=4):
    memory = [None] * frames_count  # marcos fijos
    fallos = 0
    tick = 0
    
    print("\nReferencia |", end=" ")
    for i in range(frames_count):
        print(f"Marco {i+1}".ljust(18), end=" | ")
    print("Fallo | Reset_R")
    print("-" * (13 + frames_count * 21 + 18))

    marcos_output = [[] for _ in range(frames_count)]
    fallo_row = []
    resets_row = []  # Nueva lista para tracking de resets

    for ref in ref_stream:
        page_number, op = ref.split('-')
        page_number = int(page_number)
        op = op.upper()

        tick += 1

        # Reset periódico ANTES de procesar la referencia actual
        reset_occurred = False
        if tick % reset_interval == 0:
            reset_occurred = reset_R_bits(memory)

        # Buscar si la página está en memoria
        in_memory = False
        for page in memory:
            if page is not None and page.number == page_number:
                page.R = 1
                if op == 'W':
                    page.M = 1
                page.timestamp = tick  # CORREGIDO: Actualizar timestamp en cada referencia
                in_memory = True
                break

        # Un fallo ocurre cuando una página no está presente en memoria
        # (ya sea porque el marco está vacío o porque requiere reemplazo)
        fallo = False
        if not in_memory:
            fallos += 1
            fallo = True
            
            # Buscar marco vacío
            try:
                empty_index = memory.index(None)
            except ValueError:
                empty_index = None

            if empty_index is not None:
                # Colocar en marco vacío
                memory[empty_index] = Page(page_number, R=0, M=(1 if op == 'W' else 0), timestamp=tick)
            else:
                # Algoritmo NRU: buscar víctima por clase
                classes = {0: [], 1: [], 2: [], 3: []}
                for i, page in enumerate(memory):
                    if page is not None:
                        classes[page.class_nru()].append((i, page.timestamp))
                
                # Seleccionar víctima de la clase más baja disponible
                victim_index = None
                for cls in range(4):
                    if classes[cls]:
                        # Ordenar por timestamp (más antiguo primero) y seleccionar el más antiguo
                        classes[cls].sort(key=lambda x: x[1])
                        victim_index = classes[cls][0][0]
                        break
                
                if victim_index is not None:
                    old_page = memory[victim_index]
                    print(f"    [REEMPLAZO] Página {old_page.number} (R={old_page.R}, M={old_page.M}, C={old_page.class_nru()}) → Página {page_number}")
                    new_M = 1 if op == 'W' else 0
                    memory[victim_index] = Page(page_number, R=0, M=new_M, timestamp=tick)

        # Imprimir y guardar snapshot
        snapshot = snapshot_memory(memory)
        print(f"{ref:>9} |", end=" ")
        for marco_str in snapshot:
            print(marco_str.ljust(18), end=" | ")
        print(f"{'F' if fallo else ' ':>5} | {'R' if reset_occurred else ' ':>7}")
        
        for i in range(frames_count):
            marcos_output[i].append(snapshot[i])
        fallo_row.append("F" if fallo else "X")
        resets_row.append("R" if reset_occurred else "X")  # CORREGIDO: Agregar reset tracking

    # Generar CSV con resultados - CORREGIDO: Alineación correcta
    final_csv_rows = []
    total_cols = len(ref_stream) + 1  # +1 para la columna de etiqueta
    
    final_csv_rows.append(["Numero de fallos", str(fallos)] + [""] * (total_cols - 2))
    final_csv_rows.append(["Rendimiento", f"{int(100 * (len(ref_stream) - fallos) / len(ref_stream))}%"] + [""] * (total_cols - 2))
    final_csv_rows.append(["Referencias"] + [r for r in ref_stream])
    
    for i in range(frames_count):
        final_csv_rows.append([f"Marco{i+1}"] + marcos_output[i])
    
    final_csv_rows.append(["FALLO"] + fallo_row)
    final_csv_rows.append(["RESET"] + resets_row)  # CORREGIDO: Incluir fila de resets

    with open("nru_simulacion.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(final_csv_rows)

    tasa_fallos = fallos / len(ref_stream)
    rendimiento = 100 * (len(ref_stream) - fallos) / len(ref_stream)
    return fallos, tasa_fallos, rendimiento


def print_nru_info():
    print("=== CLASES NRU ===")
    print("Clase 0: R=0, M=0 (no referenciada recientemente, no modificada) - MEJOR VÍCTIMA")
    print("Clase 1: R=0, M=1 (no referenciada recientemente, modificada)")
    print("Clase 2: R=1, M=0 (referenciada recientemente, no modificada)")
    print("Clase 3: R=1, M=1 (referenciada recientemente, modificada) - PEOR VÍCTIMA")
    print("\nReglas de reemplazo:")
    print("- Se selecciona víctima de la clase más baja disponible (0 > 1 > 2 > 3)")
    print("- Dentro de la misma clase, se selecciona la página más antigua")
    print("- Los bits R se resetean cada N accesos SOLO si no hay páginas modificadas (M=1)")


# Datos del ejemplo
referencias = [
    "2-R", "2-W", "3-R", "1-R", "1-W", "3-R", "4-W", "5-R", "1-R", "1-W", "2-R", "3-W", "4-R"
]


if __name__ == "__main__":
    print("=== SIMULACIÓN ALGORITMO NRU MEJORADO ===")
    print(f"Referencias: {len(referencias)}")
    print(f"Marcos: 4")
    print(f"Reset cada: 4 referencias")
    
    print_nru_info()
    
    fallos, tasa_fallo, rendimiento = nru_simulation(referencias, 4, reset_interval=4)
    
    print(f"\n=== RESULTADOS ===")
    print(f"Número de Fallos: {fallos}")
    print(f"Tasa de Fallos: {tasa_fallo:.4f}")
    print(f"Rendimiento (%): {rendimiento:.2f}%")
    
    print(f"\nArchivo CSV guardado: nru_simulacion.csv")
    
    print("\n=== MEJORAS IMPLEMENTADAS ===")
    print("1. ✅ Reset condicional: R se resetea SOLO si no hay páginas con M=1")
    print("2. ✅ Selección por antigüedad: dentro de la misma clase, se elige la página más antigua")
    print("3. ✅ Timestamps para tracking de antigüedad de páginas")
    print("4. ✅ Lógica de reset más fiel al algoritmo NRU teórico")
    print("5. ✅ Mejor documentación y estructura del código")
    print("6. ✅ CORREGIDO: Timestamp se actualiza en cada referencia")
    print("7. ✅ CORREGIDO: Fila de resets incluida en CSV")
    print("8. ✅ CORREGIDO: Alineación correcta de columnas en CSV")
    print("9. ✅ CORREGIDO: Reset ocurre en tick correcto (4, 8, 12...)")
    print("10. ✅ AGREGADO: Trazabilidad de reemplazos con clase NRU")
    print("11. ✅ MEJORADO: Snapshot incluye clase NRU para validación")