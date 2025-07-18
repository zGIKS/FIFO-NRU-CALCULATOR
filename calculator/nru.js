// Simulación del algoritmo de reemplazo de páginas NRU - Versión JS avanzada

class Page {
    constructor(number, R = 0, M = 0, timestamp = null) {
        this.number = number;
        this.R = R;
        this.M = M;
        this.timestamp = timestamp;
    }
    class_nru() {
        return 2 * this.R + this.M; // Clase 0 a 3
    }
    toString() {
        return `${this.number} R=${this.R} M=${this.M} T=${this.timestamp}`;
    }
}

function snapshot_memory(memory) {
    return memory.map(p => p ? `${p.number} R=${p.R} M=${p.M} C=${p.class_nru()}` : "-");
}

function reset_R_bits(memory) {
    // Resetea los bits R solo si ninguna página en memoria tiene M=1
    const has_modified_pages = memory.some(page => page && page.M === 1);
    if (has_modified_pages) return false;
    for (const page of memory) {
        if (page) page.R = 0;
    }
    return true;
}

function nru_simulation(ref_stream, frames_count, reset_interval = 4) {
    let memory = Array(frames_count).fill(null);
    let fallos = 0;
    let tick = 0;

    console.log("\nReferencia |" + Array(frames_count).fill(0).map((_,i)=>` Marco ${i+1}`.padEnd(18)).join(" | ") + " | Fallo | Reset_R");
    console.log("-".repeat(13 + frames_count * 21 + 18));

    let marcos_output = Array(frames_count).fill(0).map(()=>[]);
    let fallo_row = [];
    let resets_row = [];

    for (const ref of ref_stream) {
        let [page_number, op] = ref.split('-');
        page_number = parseInt(page_number);
        op = op.toUpperCase();
        tick++;

        // Reset periódico ANTES de procesar la referencia actual
        let reset_occurred = false;
        if (tick % reset_interval === 0) {
            reset_occurred = reset_R_bits(memory);
        }

        // Buscar si la página está en memoria
        let in_memory = false;
        for (const page of memory) {
            if (page && page.number === page_number) {
                page.R = 1;
                if (op === 'W') page.M = 1;
                page.timestamp = tick;
                in_memory = true;
                break;
            }
        }

        // Un fallo ocurre cuando una página no está presente en memoria
        let fallo = false;
        if (!in_memory) {
            fallos++;
            fallo = true;
            // Buscar marco vacío
            let empty_index = memory.indexOf(null);
            if (empty_index !== -1) {
                memory[empty_index] = new Page(page_number, 0, op === 'W' ? 1 : 0, tick);
            } else {
                // Algoritmo NRU: buscar víctima por clase
                let classes = {0: [], 1: [], 2: [], 3: []};
                for (let i = 0; i < memory.length; i++) {
                    const page = memory[i];
                    if (page) classes[page.class_nru()].push({i, t: page.timestamp});
                }
                // Seleccionar víctima de la clase más baja disponible
                let victim_index = null;
                for (let cls = 0; cls < 4; cls++) {
                    if (classes[cls].length) {
                        // Ordenar por timestamp (más antiguo primero)
                        classes[cls].sort((a, b) => a.t - b.t);
                        victim_index = classes[cls][0].i;
                        break;
                    }
                }
                if (victim_index !== null) {
                    const old_page = memory[victim_index];
                    console.log(`    [REEMPLAZO] Página ${old_page.number} (R=${old_page.R}, M=${old_page.M}, C=${old_page.class_nru()}) → Página ${page_number}`);
                    memory[victim_index] = new Page(page_number, 0, op === 'W' ? 1 : 0, tick);
                }
            }
        }

        // Imprimir y guardar snapshot
        const snapshot = snapshot_memory(memory);
        let row = ref.padStart(9) + ' |';
        for (const marco_str of snapshot) row += ' ' + marco_str.padEnd(18) + ' |';
        row += (fallo ? '    F' : '     ') + ' | ' + (reset_occurred ? '     R' : '     X');
        console.log(row);
        for (let i = 0; i < frames_count; i++) marcos_output[i].push(snapshot[i]);
        fallo_row.push(fallo ? 'F' : 'X');
        resets_row.push(reset_occurred ? 'R' : 'X');
    }

    // Generar CSV como string
    let final_csv_rows = [];
    const total_cols = ref_stream.length + 1;
    final_csv_rows.push(["Numero de fallos", String(fallos), ...Array(total_cols - 2).fill("")]);
    final_csv_rows.push(["Rendimiento", `${Math.round(100 * (ref_stream.length - fallos) / ref_stream.length)}%`, ...Array(total_cols - 2).fill("")]);
    final_csv_rows.push(["Referencias", ...ref_stream]);
    for (let i = 0; i < frames_count; i++) final_csv_rows.push([`Marco${i+1}`, ...marcos_output[i]]);
    final_csv_rows.push(["FALLO", ...fallo_row]);
    final_csv_rows.push(["RESET", ...resets_row]);

    // Convertir a string CSV
    function toCSV(rows) {
        return rows.map(r => r.join(",")).join("\n");
    }
    const csvString = toCSV(final_csv_rows);

    const tasa_fallos = fallos / ref_stream.length;
    const rendimiento = 100 * (ref_stream.length - fallos) / ref_stream.length;
    return {fallos, tasa_fallos, rendimiento, csvString};
}

function print_nru_info() {
    console.log("=== CLASES NRU ===");
    console.log("Clase 0: R=0, M=0 (no referenciada recientemente, no modificada) - MEJOR VÍCTIMA");
    console.log("Clase 1: R=0, M=1 (no referenciada recientemente, modificada)");
    console.log("Clase 2: R=1, M=0 (referenciada recientemente, no modificada)");
    console.log("Clase 3: R=1, M=1 (referenciada recientemente, modificada) - PEOR VÍCTIMA");
    console.log("\nReglas de reemplazo:");
    console.log("- Se selecciona víctima de la clase más baja disponible (0 > 1 > 2 > 3)");
    console.log("- Dentro de la misma clase, se selecciona la página más antigua");
    console.log("- Los bits R se resetean cada N accesos SOLO si no hay páginas modificadas (M=1)");
}

(function() {
// Datos del ejemplo
const referencias = [
    "2-R", "2-W", "3-R", "1-R", "1-W", "3-R", "4-W", "5-R", "1-R", "1-W", "2-R", "3-W", "4-R"
];

// MAIN
console.log("=== SIMULACIÓN ALGORITMO NRU MEJORADO ===");
console.log(`Referencias: ${referencias.length}`);
console.log(`Marcos: 4`);
console.log(`Reset cada: 4 referencias`);

print_nru_info();

const {fallos, tasa_fallos, rendimiento, csvString} = nru_simulation(referencias, 4, 4);

console.log(`\n=== RESULTADOS ===`);
console.log(`Número de Fallos: ${fallos}`);
console.log(`Tasa de Fallos: ${tasa_fallos.toFixed(4)}`);
console.log(`Rendimiento (%): ${rendimiento.toFixed(2)}%`);

console.log(`\n=== CONTENIDO DEL CSV ===`);
console.log(csvString);

// --- DESCARGA CSV Y EXCEL ---
if (typeof window !== 'undefined') {
    // Botón para descargar CSV
    let btnCsv = document.createElement('button');
    btnCsv.textContent = 'Descargar CSV NRU';
    btnCsv.onclick = function() {
        const blob = new Blob([csvString], {type: 'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'nru_resultado.csv';
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>{document.body.removeChild(a); URL.revokeObjectURL(url);}, 100);
    };
    document.body.appendChild(btnCsv);

    // Botón para descargar Excel (requiere SheetJS)
    let btnXlsx = document.createElement('button');
    btnXlsx.textContent = 'Descargar Excel NRU';
    btnXlsx.onclick = function() {
        if (typeof XLSX === 'undefined') {
            alert('SheetJS (XLSX) no está cargado.');
            return;
        }
        // Convertir csvString a array de filas
        const rows = csvString.split('\n').map(r => r.split(','));
        const ws = XLSX.utils.aoa_to_sheet(rows);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'NRU');
        XLSX.writeFile(wb, 'nru_resultado.xlsx');
    };
    document.body.appendChild(btnXlsx);
}

console.log("\n=== MEJORAS IMPLEMENTADAS ===");
console.log("1. ✅ Reset condicional: R se resetea SOLO si no hay páginas con M=1");
console.log("2. ✅ Selección por antigüedad: dentro de la misma clase, se elige la página más antigua");
console.log("3. ✅ Timestamps para tracking de antigüedad de páginas");
console.log("4. ✅ Lógica de reset más fiel al algoritmo NRU teórico");
console.log("5. ✅ Mejor documentación y estructura del código");
console.log("6. ✅ CORREGIDO: Timestamp se actualiza en cada referencia");
console.log("7. ✅ CORREGIDO: Fila de resets incluida en CSV");
console.log("8. ✅ CORREGIDO: Alineación correcta de columnas en CSV");
console.log("9. ✅ CORREGIDO: Reset ocurre en tick correcto (4, 8, 12...)");
console.log("10. ✅ AGREGADO: Trazabilidad de reemplazos con clase NRU");
console.log("11. ✅ MEJORADO: Snapshot incluye clase NRU para validación");
})();
