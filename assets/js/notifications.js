function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    
    // Style directly for speed
    Object.assign(toast.style, {
        background: type === 'error' ? '#f85149' : '#3fb950',
        color: 'white',
        padding: '12px 20px',
        borderRadius: '6px',
        marginBottom: '10px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        transition: '0.3s'
    });

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}