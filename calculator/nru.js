// NRU Mejorado en JS
class Page {
    constructor(number, R = 0, M = 0, timestamp = null) {
        this.number = number;
        this.R = R;
        this.M = M;
        this.timestamp = timestamp;
    }
    class_nru() {
        return 2 * this.R + this.M;
    }
    toString() {
        return `${this.number} R=${this.R} M=${this.M} T=${this.timestamp}`;
    }
}

function snapshotMemory(memory) {
    return memory.map(p => p ? p.toString() : "-");
}

function resetRBits(memory) {
    // Solo si ninguna página tiene M=1
    const hasModified = memory.some(page => page && page.M === 1);
    if (hasModified) return false;
    memory.forEach(page => { if (page) page.R = 0; });
    return true;
}

function nruSimulation(refStream, framesCount, resetInterval = 4) {
    const memory = Array(framesCount).fill(null);
    let fallos = 0;
    let tick = 0;
    const marcosOutput = Array(framesCount).fill(0).map(() => []);
    const falloRow = [];
    const resultTable = [];

    refStream.forEach(ref => {
        const [pageStr, op] = ref.split('-');
        const pageNumber = parseInt(pageStr);
        const opU = op.toUpperCase();
        tick++;

        // Reset condicional
        let resetOccurred = false;
        if ((tick - 1) % resetInterval === 0 && tick !== 1) {
            resetOccurred = resetRBits(memory);
        }

        // Buscar si la página está en memoria
        let inMemory = false;
        for (const page of memory) {
            if (page && page.number === pageNumber) {
                page.R = 1;
                if (opU === 'W') page.M = 1;
                inMemory = true;
                break;
            }
        }

        let fallo = false;
        if (!inMemory) {
            fallos++;
            fallo = true;
            let emptyIndex = memory.indexOf(null);
            if (emptyIndex !== -1) {
                memory[emptyIndex] = new Page(pageNumber, 1, opU === 'W' ? 1 : 0, tick);
            } else {
                // NRU: por clase y antigüedad
                const classes = {0: [], 1: [], 2: [], 3: []};
                memory.forEach((page, i) => {
                    if (page) classes[page.class_nru()].push({i, t: page.timestamp});
                });
                let victimIndex = null;
                for (let cls = 0; cls < 4; cls++) {
                    if (classes[cls].length) {
                        // Más antiguo primero
                        classes[cls].sort((a, b) => a.t - b.t);
                        victimIndex = classes[cls][0].i;
                        break;
                    }
                }
                if (victimIndex !== null) {
                    memory[victimIndex] = new Page(pageNumber, 1, opU === 'W' ? 1 : 0, tick);
                }
            }
        }

        // Guardar snapshot
        const snapshot = snapshotMemory(memory);
        snapshot.forEach((val, i) => marcosOutput[i].push(val));
        falloRow.push(fallo ? "F" : "X");
        resultTable.push({ref, snapshot, fallo, resetOccurred});
    });

    // Construir tabla tipo CSV
    const finalRows = [];
    finalRows.push(["Numero de fallos", fallos, ...Array(refStream.length - 1).fill("")]);
    finalRows.push(["Rendimiento", `${Math.round(100 * (refStream.length - fallos) / refStream.length)}%`, ...Array(refStream.length - 1).fill("")]);
    finalRows.push(["Tasa de fallos", (fallos / refStream.length).toFixed(4), ...Array(refStream.length - 1).fill("")]);
    finalRows.push(["", ...refStream]);
    for (let i = 0; i < framesCount; i++) {
        finalRows.push([`Marco${i+1}`, ...marcosOutput[i]]);
    }
    finalRows.push(["FALLO", ...falloRow]);

    return {fallos, rendimiento: Math.round(100 * (refStream.length - fallos) / refStream.length), tasaFallos: (fallos / refStream.length).toFixed(4), finalRows, resultTable};
}

window.nruSimulation = nruSimulation;
