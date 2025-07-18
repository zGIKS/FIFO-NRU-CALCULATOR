# Simulador de Algoritmos de Reemplazo de Páginas: FIFO y NRU

Este proyecto es una calculadora web interactiva para simular y comparar los algoritmos de reemplazo de páginas FIFO y NRU. Permite ingresar referencias, número de marcos y parámetros específicos, mostrando resultados paso a paso, métricas y exportando el resultado en formato CSV.

## Características
- Simulación visual y detallada de los algoritmos FIFO y NRU.
- Interfaz web moderna y responsiva.
- Permite cambiar entre algoritmos con un solo clic.
- Resultados en tabla, métricas de fallos y rendimiento.
- Exportación de resultados en formato CSV.
- Soporte para referencias personalizadas y parámetros de simulación.

## Estructura del Proyecto
```
calculator/
├── index.html        # Interfaz principal de la calculadora web
├── style.css         # Estilos modernos y responsivos
├── fifo.js           # Lógica del algoritmo FIFO en JS
├── nru.js            # Lógica del algoritmo NRU en JS
```

## Uso
1. Abre `index.html` en tu navegador web.
2. Selecciona el algoritmo (FIFO o NRU) usando los botones superiores.
3. Ingresa la secuencia de referencias y el número de marcos.
   - Para NRU, también puedes definir el intervalo de reset y referencias con R/W.
4. Haz clic en **Simular**.
5. Visualiza la tabla de resultados, métricas y descarga el CSV si lo deseas.

## Ejemplo de Referencias
- **FIFO:** `X,Y,Z,W,X,Y,L,X,Y,Z,W,L`
- **NRU:** `2-R,2-W,3-R,1-R,1-W,3-R,4-W,5-R,1-R,1-W,2-R,3-W,4-R`

## Requisitos
- Navegador web moderno (Chrome, Firefox, Edge, etc.)
- No requiere instalación ni dependencias externas.

## Créditos
Desarrollado por zGIKS. Inspirado en prácticas de sistemas operativos y algoritmos de memoria.

---
¡Explora, aprende y experimenta con los algoritmos de reemplazo de páginas!
