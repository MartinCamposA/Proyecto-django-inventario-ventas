// ─── Cierre automático de alertas ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('[data-alert]');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });
});

// ─── Mantener foco en el scanner después de cada acción HTMX ─────────────
document.addEventListener('htmx:afterSwap', function () {
    const skuInput = document.getElementById('sku-input');
    if (skuInput) skuInput.focus();
});

// ─── Cerrar modal con Escape ──────────────────────────────────────────────
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        cerrarModal();
    }
    if (e.key === 'F1') {
        e.preventDefault();
        const skuInput = document.getElementById('sku-input');
        if (skuInput) skuInput.focus();
    }
});

// ─── Funciones del modal ──────────────────────────────────────────────────
function cerrarModal() {
    const modal = document.getElementById('payment-modal-container');
    if (modal) {
        modal.classList.add('hidden');
        modal.innerHTML = '';
    }
    const skuInput = document.getElementById('sku-input');
    if (skuInput) skuInput.focus();
}

function abrirModal() {
    const modal = document.getElementById('payment-modal-container');
    if (modal) modal.classList.remove('hidden');
}

// ─── Calcular vuelto ──────────────────────────────────────────────────────
function calcularVuelto(montoRecibido, total) {
    const monto = parseFloat(montoRecibido) || 0;
    const vuelto = monto - parseFloat(total);
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