// NRU Algorithm in JS
class Page {
    constructor(number, R = 0, M = 0) {
        this.number = number;
        this.R = R;
        this.M = M;
    }
    class_nru() {
        return 2 * this.R + this.M;
    }
    toString() {
        return `${this.number} R=${this.R} M=${this.M}`;
    }
}

function snapshotMemory(memory) {
    return memory.map(p => p ? p.toString() : "-");
}

function resetRBits(memory) {
    memory.forEach(page => {
        if (page) page.R = 0;
    });
}

function nruSimulation(refStream, framesCount, resetInterval = 4) {
    const memory = Array(framesCount).fill(null);
    let fallos = 0;
    let refCounter = 0;
    const marcosOutput = Array(framesCount).fill(0).map(() => []);
    const falloRow = [];
    const resultTable = [];

    refStream.forEach(ref => {
        const [pageStr, op] = ref.split('-');
        const pageNumber = parseInt(pageStr);
        const opU = op.toUpperCase();
        refCounter++;

        // Reset R bits
        let resetOccurred = false;
        if ((refCounter - 1) % resetInterval === 0 && refCounter !== 1) {
            resetRBits(memory);
            resetOccurred = true;
        }

        // Check if page is in memory
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
                memory[emptyIndex] = new Page(pageNumber, 1, opU === 'W' ? 1 : 0);
            } else {
                // NRU victim selection
                const classes = {0: [], 1: [], 2: [], 3: []};
                memory.forEach((page, i) => {
                    if (page) classes[page.class_nru()].push(i);
                });
                let victimIndex = null;
                for (let cls = 0; cls < 4; cls++) {
                    if (classes[cls].length) {
                        victimIndex = classes[cls][0];
                        break;
                    }
                }
                if (victimIndex !== null) {
                    memory[victimIndex] = new Page(pageNumber, 1, opU === 'W' ? 1 : 0);
                }
            }
        }

        // Save snapshot
        const snapshot = snapshotMemory(memory);
        snapshot.forEach((val, i) => marcosOutput[i].push(val));
        falloRow.push(fallo ? "F" : "X");
        resultTable.push({ref, snapshot, fallo, resetOccurred});
    });

    // Build CSV-like output
    const finalRows = [];
    finalRows.push(["Numero de fallos", fallos, ...Array(refStream.length - 1).fill("")]);
    finalRows.push(["Rendimiento", `${Math.round(100 * (refStream.length - fallos) / refStream.length)}%`, ...Array(refStream.length - 1).fill("")]);
    finalRows.push(["", ...refStream]);
    for (let i = 0; i < framesCount; i++) {
        finalRows.push([`Marco${i+1}`, ...marcosOutput[i]]);
    }
    finalRows.push(["FALLO", ...falloRow]);

    return {fallos, rendimiento: Math.round(100 * (refStream.length - fallos) / refStream.length), finalRows, resultTable};
}

// Export for use in HTML
window.nruSimulation = nruSimulation;
