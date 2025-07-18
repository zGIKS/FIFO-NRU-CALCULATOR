// Simulación del algoritmo de reemplazo de páginas FIFO - Versión JS

// Secuencia de referencias de páginas
const referencias = ["X", "Y", "Z", "W", "X", "Y", "L", "X", "Y", "Z", "W", "L"];
const marcos = 4; // Número de marcos disponibles

// Inicialización
let memoria = []; // Lista de páginas en memoria
let cola_fifo = []; // Cola FIFO para el orden de llegada
let fallos = []; // Lista de "SI" o "NO" indicando si hubo fallo de página
let estados_memoria = []; // Lista para guardar el estado de los marcos en cada instante

console.log("=== SIMULACIÓN PASO A PASO ===");
let header = "Instante | Referencia ";
for (let i = 0; i < marcos; i++) header += `| Marco ${i} `;
header += "| Fallo | Acción";
console.log(header);
console.log("-".repeat(header.length));

// Simulación de FIFO
for (let i = 0; i < referencias.length; i++) {
    const pagina = referencias[i];
    let accion = "";
    if (memoria.includes(pagina)) {
        fallos.push("X"); // Hit
        accion = "Hit - página ya en memoria";
    } else {
        fallos.push("F"); // Fallo
        if (memoria.length < marcos) {
            memoria.push(pagina);
            cola_fifo.push(pagina);
            accion = `Cargar en marco ${memoria.length - 1}`;
        } else {
            const pagina_reemplazar = cola_fifo.shift();
            const idx = memoria.indexOf(pagina_reemplazar);
            memoria[idx] = pagina;
            cola_fifo.push(pagina);
            accion = `Reemplazar ${pagina_reemplazar} por ${pagina} en marco ${idx}`;
        }
    }
    // Guardar snapshot del estado de los marcos
    let snapshot = memoria.slice();
    while (snapshot.length < marcos) snapshot.push("-");
    estados_memoria.push(snapshot);
    // Mostrar estado actual (dinámico según número de marcos)
    let linea = `   ${(i+1).toString().padStart(2)}    |     ${pagina}      `;
    for (let val of snapshot) linea += `|    ${val}    `;
    linea += `|  ${fallos[i]}   | ${accion}`;
    console.log(linea);
}

// Construcción del arreglo de resultados
let resultado = [];
for (let i = 0; i < referencias.length; i++) {
    let fila = [`Instante ${i+1}`, referencias[i]];
    fila = fila.concat(estados_memoria[i]);
    fila.push(fallos[i]);
    resultado.push(fila);
}

console.log("\n=== ARREGLO DE RESULTADOS ===");
let cabecera = ["Instante", "Referencia"];
for (let i = 0; i < marcos; i++) cabecera.push(`Marco ${i}`);
cabecera.push("Fallo");
console.log(JSON.stringify(cabecera));
for (let fila of resultado) {
    console.log(JSON.stringify(fila));
}

// Mostrar resumen de resultados
const num_fallos = fallos.filter(f => f === "F").length;
const tasa_fallos = num_fallos / referencias.length;
const rendimiento = 100 * (referencias.length - num_fallos) / referencias.length;

console.log("\n=== RESULTADOS FINALES ===");
console.log(`Número de Referencias: ${referencias.length}`);
console.log(`Número de Fallos: ${num_fallos}`);
console.log(`Tasa de Fallos: ${tasa_fallos.toFixed(4)}`);
console.log(`Rendimiento (%): ${rendimiento.toFixed(2)}%`);

// Verificación de integridad
console.log("\n=== VERIFICACIÓN DE INTEGRIDAD ===");
console.log(`Estado final de memoria: ${JSON.stringify(memoria)}`);
console.log(`Estado final de cola FIFO: ${JSON.stringify(cola_fifo)}`);

// Análisis adicional
console.log("\n=== ANÁLISIS DETALLADO ===");
console.log("Secuencia de fallos por página:");
for (let i = 0; i < referencias.length; i++) {
    let estado = fallos[i] === "F" ? "FALLO" : "HIT";
    console.log(`  ${referencias[i]}: ${estado}`);
}

// ===============================
// GENERACIÓN DEL ARCHIVO CSV (como string)
// ===============================

function generarCSV() {
    let csv = '';
    // Cabeceras de estadísticas
    csv += ['Numero de fallos', num_fallos, ...Array(referencias.length-1).fill('')].join(',') + '\n';
    csv += ['Rendimiento', `${rendimiento.toFixed(0)}%`, ...Array(referencias.length-1).fill('')].join(',') + '\n';
    // Fila de referencias
    csv += ['Referencias', ...referencias].join(',') + '\n';
    // Estados de marcos
    for (let i = 0; i < marcos; i++) {
        let fila = [`Marco${i+1}`];
        for (let j = 0; j < referencias.length; j++) {
            fila.push(estados_memoria[j][i]);
        }
        csv += fila.join(',') + '\n';
    }
    // Fallos
    csv += ['FALLO', ...fallos].join(',') + '\n';
    // Reset (no aplica, pero se mantiene formato)
    csv += ['RESET', ...Array(referencias.length).fill('X')].join(',') + '\n';
    return csv;
}

const csvString = generarCSV();
console.log("\n=== CONTENIDO DEL CSV ===");
console.log(csvString);
