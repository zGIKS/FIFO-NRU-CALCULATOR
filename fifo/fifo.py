import csv

# Simulación del algoritmo de reemplazo de páginas FIFO - Versión Corregida

# Secuencia de referencias de páginas
referencias = ["X", "Y", "Z", "W", "X", "Y", "L", "X", "Y", "Z", "W", "L"]
marcos = 4  # Número de marcos disponibles

# Inicialización
memoria = []  # Lista de páginas en memoria
cola_fifo = []  # Cola FIFO para el orden de llegada
fallos = []  # Lista de "SI" o "NO" indicando si hubo fallo de página
estados_memoria = []  # Lista para guardar el estado de los marcos en cada instante

print("=== SIMULACIÓN PASO A PASO ===")
print("Instante | Referencia | Marco 0 | Marco 1 | Marco 2 | Marco 3 | Fallo | Acción")
print("-" * 80)

# Simulación de FIFO
for i, pagina in enumerate(referencias):
    accion = ""
    
    if pagina in memoria:
        # Página ya está en memoria - no hay fallo
        fallos.append("X")  # Cambio a "X" para el CSV
        accion = "Hit - página ya en memoria"
    else:
        # Página no está en memoria - hay fallo
        fallos.append("F")  # Cambio a "F" para el CSV
        
        if len(memoria) < marcos:
            # Hay espacio disponible
            memoria.append(pagina)
            cola_fifo.append(pagina)
            accion = f"Cargar en marco {len(memoria)-1}"
        else:
            # No hay espacio - reemplazo FIFO
            pagina_reemplazar = cola_fifo.pop(0)  # La más antigua
            
            idx = memoria.index(pagina_reemplazar)
            memoria[idx] = pagina
            cola_fifo.append(pagina)
            accion = f"Reemplazar {pagina_reemplazar} por {pagina} en marco {idx}"

    # Guardar snapshot del estado de los marcos
    snapshot = memoria.copy()
    while len(snapshot) < marcos:
        snapshot.append("-")
    estados_memoria.append(snapshot)
    
    # Mostrar estado actual (dinámico según número de marcos)
    linea = f"   {i+1:2d}    |     {pagina}      "
    for val in snapshot:
        linea += f"|    {val}    "
    # Si hay menos de 4 marcos, completa con '-'
    for _ in range(4 - len(snapshot)):
        linea += f"|    -    "
    linea += f"|  {fallos[i]}   | {accion}"
    print(linea)

# Construcción del arreglo de resultados
resultado = []
for i in range(len(referencias)):
    fila = [f"Instante {i+1}", referencias[i]]
    fila.extend(estados_memoria[i])
    # Completa con '-' si hay menos de 4 marcos
    for _ in range(4 - len(estados_memoria[i])):
        fila.append('-')
    fila.append(fallos[i])
    resultado.append(fila)

print("\n=== ARREGLO DE RESULTADOS ===")
print("['Instante', 'Referencia', 'Marco 0', 'Marco 1', 'Marco 2', 'Marco 3', 'Fallo']")
for fila in resultado:
    print(f"{fila},")

# Mostrar resumen de resultados
num_fallos = fallos.count("F")
tasa_fallos = num_fallos / len(referencias)
rendimiento = 100 * (len(referencias) - num_fallos) / len(referencias)

print("\n=== RESULTADOS FINALES ===")
print(f"Número de Referencias: {len(referencias)}")
print(f"Número de Fallos: {num_fallos}")
print(f"Tasa de Fallos: {tasa_fallos:.4f}")
print(f"Rendimiento (%): {rendimiento:.2f}%")

# Verificación de integridad
print("\n=== VERIFICACIÓN DE INTEGRIDAD ===")
print(f"Estado final de memoria: {memoria}")
print(f"Estado final de cola FIFO: {cola_fifo}")
# Esta comparación puede ser falsa incluso si el algoritmo es correcto
# Mejor mostrar ambas listas para inspección manual

# Análisis adicional
print("\n=== ANÁLISIS DETALLADO ===")
print("Secuencia de fallos por página:")
for i, ref in enumerate(referencias):
    estado = "FALLO" if fallos[i] == "F" else "HIT"
    print(f"  {ref}: {estado}")

# ===============================
# GENERACIÓN DEL ARCHIVO CSV
# ===============================

filename = "simulacion_fifo.csv"
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Escribir cabeceras de estadísticas
    writer.writerow(['Numero de fallos', num_fallos] + [''] * (len(referencias) - 1))
    writer.writerow(['Rendimiento', f'{rendimiento:.0f}%'] + [''] * (len(referencias) - 1))
    
    # Escribir fila de referencias
    writer.writerow(['Referencias'] + referencias)
    
    # Escribir estados de marcos
    for i in range(marcos):
        fila = [f'Marco{i+1}']
        for j in range(len(referencias)):
            fila.append(estados_memoria[j][i])
        writer.writerow(fila)
    
    # Escribir fallos
    writer.writerow(['FALLO'] + fallos)
    
    # Escribir información de reset (no aplica para FIFO, pero mantenemos el formato)
    writer.writerow(['RESET'] + ['X'] * len(referencias))

print(f"\n=== ARCHIVO CSV GENERADO ===")
print(f"Archivo guardado como: {filename}")

# Mostrar el contenido del CSV generado
print(f"\n=== CONTENIDO DEL CSV ===")
with open(filename, 'r', encoding='utf-8') as csvfile:
    contenido = csvfile.read()
    print(contenido)