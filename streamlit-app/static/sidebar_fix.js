// Sidebar Accessibility Fix for Streamlit
// This script ensures the sidebar remains accessible when toggled

(function() {
    'use strict';
    
    function fixSidebarAccessibility() {
        // Find sidebar element
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const sidebarContainer = document.querySelector('.css-1d391kg');
        const toggleButtons = document.querySelectorAll('button[title*="sidebar"]');
        
        if (sidebar) {
            // Ensure sidebar has proper styling
            sidebar.style.zIndex = '999999';
            sidebar.style.position = 'relative';
            sidebar.style.minWidth = '300px';
            
            // Remove any problematic styles that might hide the sidebar
            if (sidebar.style.display === 'none') {
                sidebar.style.display = 'block';
            }
            if (sidebar.style.visibility === 'hidden') {
                sidebar.style.visibility = 'visible';
            }
            if (sidebar.style.opacity === '0') {
                sidebar.style.opacity = '1';
            }
            
            // Ensure sidebar container is visible
            if (sidebarContainer) {
                sidebarContainer.style.display = 'block';
                sidebarContainer.style.visibility = 'visible';
                sidebarContainer.style.opacity = '1';
            }
        }
        
        // Ensure toggle buttons are accessible
        toggleButtons.forEach(button => {
            if (button) {
                button.style.zIndex = '1000000';
                button.style.position = 'relative';
                button.style.display = 'block';
                button.style.visibility = 'visible';
            }
        });
        
        // Add click event listeners to toggle buttons to ensure they work
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                setTimeout(fixSidebarAccessibility, 100);
            });
        });
    }
    
    // Run fixes when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixSidebarAccessibility);
    } else {
        fixSidebarAccessibility();
    }
    
    // Run fixes periodically to handle dynamic changes
    setInterval(fixSidebarAccessibility, 1000);
    
    // Run fixes when window is resized
    window.addEventListener('resize', fixSidebarAccessibility);
    
    // Observer to watch for DOM changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'attributes') {
                fixSidebarAccessibility();
            }
        });
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    
    console.log('Sidebar accessibility fix loaded');
})();
