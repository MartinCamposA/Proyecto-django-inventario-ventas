// ─── Calculadora de vuelto en tiempo real ────────────────────────────────
function calcularVuelto(montoRecibido) {
    const totalElement = document.getElementById('cart-total-value');
    if (!totalElement) return;

    const total = parseFloat(totalElement.dataset.total || 0);
    const monto = parseFloat(montoRecibido) || 0;
    const vuelto = monto - total;

    const display = document.getElementById('change-display');
    if (!display) return;

    if (vuelto >= 0) {
        display.textContent = '$' + Math.round(vuelto).toLocaleString('es-CL');
        display.className = 'text-2xl font-bold text-green-600';
    } else {
        display.textContent = 'Monto insuficiente';
        display.className = 'text-2xl font-bold text-red-500';
    }
}

// ─── Atajos de teclado en la pantalla de caja ────────────────────────────
document.addEventListener('keydown', function (e) {
    // Escape: cierra el modal de pago
    if (e.key === 'Escape') {
        const modal = document.getElementById('payment-modal-container');
        if (modal) modal.classList.add('hidden');
        const skuInput = document.getElementById('sku-input');
        if (skuInput) skuInput.focus();
    }

    // F1: foco al input del scanner
    if (e.key === 'F1') {
        e.preventDefault();
        const skuInput = document.getElementById('sku-input');
        if (skuInput) skuInput.focus();
    }
});