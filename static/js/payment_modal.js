const total = {{ cart_total }};
function calcularVuelto(monto) {
    const vuelto = parseFloat(monto) - total;
    const display = document.getElementById('change-display');
    if (vuelto >= 0) {
        display.textContent = '$' + Math.round(vuelto).toLocaleString('es-CL');
        display.classList.remove('text-red-600');
        display.classList.add('text-green-600');
    } else {
        display.textContent = 'Monto insuficiente';
        display.classList.remove('text-green-600');
        display.classList.add('text-red-600');
    }
}