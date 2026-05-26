// ─── Cierre automático de mensajes de alerta ──────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('[data-alert]');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000); // Se cierra a los 3 segundos
    });
});

// ─── HTMX: mantener el foco en el input del scanner ──────────────────────
document.addEventListener('htmx:afterSwap', function (event) {
    const skuInput = document.getElementById('sku-input');
    if (skuInput) {
        skuInput.focus();
    }
});

// ─── HTMX: cerrar modal después de confirmar venta ───────────────────────
document.addEventListener('htmx:afterRequest', function (event) {
    if (event.detail.pathInfo &&
        event.detail.pathInfo.requestPath === '/ventas/caja/confirmar/') {
        const modal = document.getElementById('payment-modal-container');
        if (modal) {
            modal.classList.add('hidden');
        }
    }
});