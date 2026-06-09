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
    const inner = document.getElementById('payment-modal-inner');
    if (modal) modal.classList.add('hidden');
    if (inner) inner.innerHTML = '';
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

// ─── Validar formulario antes de enviar ──────────────────────────────────
function validarFormulario(form) {
    const paymentMethod = form.querySelector('[name="payment_method"]').value;

    if (paymentMethod === "CASH") {
        const montoInput = form.querySelector('[name="amount_tendered"]');
        const total = parseFloat(montoInput.getAttribute("min"));
        const monto = parseFloat(montoInput.value) || 0;
        const errorMsg = document.getElementById("monto-error");

        if (monto < total || montoInput.value === "") {
            // Mostrar error
            errorMsg.classList.remove("hidden");
            montoInput.classList.add("border-red-400");
            montoInput.classList.remove("border-gray-300");
            montoInput.focus();
            return false; // Bloquea el envío del formulario
        }

        // Si está bien, ocultar error
        errorMsg.classList.add("hidden");
        montoInput.classList.remove("border-red-400");
        montoInput.classList.add("border-gray-300");
    }

    return true; // Permite el envío
}

// ─── Actualizar calcularVuelto para mostrar error en tiempo real ──────────
function calcularVuelto(montoRecibido, total) {
    const monto = parseFloat(montoRecibido) || 0;
    const totalNum = parseFloat(total);
    const vuelto = monto - totalNum;
    const display = document.getElementById('change-display');
    const errorMsg = document.getElementById("monto-error");
    const montoInput = document.getElementById("amount-tendered");
    const btnConfirmar = document.getElementById("btn-confirmar");

    if (!display) return;

    if (vuelto >= 0) {
        // Monto válido
        display.textContent = '$' + Math.round(vuelto).toLocaleString('es-CL');
        display.className = 'text-2xl font-bold text-green-600';

        if (errorMsg) errorMsg.classList.add("hidden");
        if (montoInput) {
            montoInput.classList.remove("border-red-400");
            montoInput.classList.add("border-gray-300");
        }
        if (btnConfirmar) {
            btnConfirmar.disabled = false;
            btnConfirmar.classList.remove("opacity-50", "cursor-not-allowed");
        }
    } else {
        // Monto insuficiente
        display.textContent = 'Monto insuficiente';
        display.className = 'text-2xl font-bold text-red-500';

        if (errorMsg) errorMsg.classList.remove("hidden");
        if (montoInput) {
            montoInput.classList.add("border-red-400");
            montoInput.classList.remove("border-gray-300");
        }
        if (btnConfirmar) {
            btnConfirmar.disabled = true;
            btnConfirmar.classList.add("opacity-50", "cursor-not-allowed");
        }
    }
}
// ─── Redirigir al login si HTMX recibe un 302 hacia /login/ ──────────────
document.addEventListener('htmx:beforeSwap', function (event) {
    if (event.detail.xhr.status === 403 ||
        event.detail.xhr.responseURL.includes('/login/')) {
        event.preventDefault();
        window.location.href = '/login/';
    }
});