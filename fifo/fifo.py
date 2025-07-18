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
print("Instante | Referencia | Marco 0 | Marco 1 | Marco 2 | Fallo | Acción")
print("-" * 70)

# Simulación de FIFO
for i, pagina in enumerate(referencias):
    accion = ""
    
    if pagina in memoria:
        # Página ya está en memoria - no hay fallo
        fallos.append("NO")
        accion = "Hit - página ya en memoria"
    else:
        # Página no está en memoria - hay fallo
        fallos.append("SI")
        
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
    
    # Mostrar estado actual
    print(f"   {i+1:2d}    |     {pagina}      |    {snapshot[0]}    |    {snapshot[1]}    |    {snapshot[2]}    |  {fallos[i]}   | {accion}")

# Construcción del arreglo de resultados
resultado = []
for i in range(len(referencias)):
    fila = [
        f"Instante {i+1}",
        referencias[i],
        estados_memoria[i][0],
        estados_memoria[i][1],
        estados_memoria[i][2],
        fallos[i]
    ]
    resultado.append(fila)

print("\n=== ARREGLO DE RESULTADOS ===")
print("['Instante', 'Referencia', 'Marco 0', 'Marco 1', 'Marco 2', 'Fallo']")
for fila in resultado:
    print(f"{fila},")

# Mostrar resumen de resultados
num_fallos = fallos.count("SI")
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
    estado = "FALLO" if fallos[i] == "SI" else "HIT"
    print(f"  {ref}: {estado}")