function toggleSidebar() {
    const sidebar = window.parent.document.querySelector("section[data-testid='stSidebar']");
    const sidebarButton = window.parent.document.querySelector("[data-testid='collapsedControl']");
    
    if (sidebar && sidebarButton) {
        if (sidebar.style.display === 'none') {
            sidebar.style.display = 'block';
            sidebarButton.style.left = '21rem';
        } else {
            sidebar.style.display = 'none';
            sidebarButton.style.left = '0px';
        }
        
        sidebarButton.style.display = 'block';
        sidebarButton.style.visibility = 'visible';
    }
    
    // Disparar evento de redimensionamento após a operação
    window.dispatchEvent(new Event('resize'));
}
setTimeout(toggleSidebar, 100);
