/**
 * V3 Debug Helper
 * 
 * Provides debugging utilities for the V3 Interactive Scraper
 * Can be called from browser console to diagnose issues
 */

// Global debug function
window.v3Debug = function() {
    console.log('🔧 V3 Interactive Scraper Debug Report');
    console.log('=====================================');
    
    // Check overlay status
    const overlay = window.V3InteractiveOverlay || window.v3InteractiveOverlay;
    console.log('🎯 Overlay Status:');
    console.log('  Class available:', !!window.V3InteractiveOverlay);
    console.log('  Instance available:', !!window.v3InteractiveOverlay);
    console.log('  Is active:', overlay ? overlay.state?.isActive : 'N/A');
    console.log('  Current mode:', overlay ? overlay.state?.mode : 'N/A');
    
    // Check UI elements
    console.log('\n🎨 UI Elements:');
    console.log('  Overlay container:', !!document.querySelector('#v3-interactive-overlay'));
    console.log('  Toolbar:', !!document.querySelector('#v3-toolbar'));
    console.log('  Sidebar:', !!document.querySelector('#v3-sidebar'));
    console.log('  Inspector:', !!document.querySelector('#v3-inspector'));
    
    // Check other components
    console.log('\n🤖 Other Components:');
    console.log('  Auto-detector:', !!window.V3AutoDetector || !!window.AutoDetector);
    console.log('  Communication bridge:', !!window.v3CommunicationBridge || !!window.v3Bridge);
    
    // Check for errors
    console.log('\n❌ Recent Errors:');
    const errors = window.v3Errors || [];
    if (errors.length > 0) {
        errors.forEach((error, index) => {
            console.log(`  ${index + 1}. ${error}`);
        });
    } else {
        console.log('  No errors recorded');
    }
    
    // Check page state
    console.log('\n📄 Page State:');
    console.log('  URL:', window.location.href);
    console.log('  Ready state:', document.readyState);
    console.log('  DOM elements:', document.querySelectorAll('*').length);
    
    // Provide solutions
    console.log('\n🔧 Quick Fixes:');
    console.log('  1. Force start overlay: window.v3ForceStart()');
    console.log('  2. Reset overlay: window.v3Reset()');
    console.log('  3. Show fallback toolbar: window.v3Fallback()');
    console.log('  4. Manual overlay creation: new window.V3InteractiveOverlay()');
    
    return {
        overlay: !!overlay,
        active: overlay ? overlay.state?.isActive : false,
        toolbar: !!document.querySelector('#v3-toolbar'),
        errors: window.v3Errors || []
    };
};

// Force start function
window.v3ForceStart = function() {
    console.log('🚀 Force starting V3 Interactive Overlay...');
    
    try {
        let overlay = window.v3InteractiveOverlay;
        
        if (!overlay) {
            if (window.V3InteractiveOverlay) {
                overlay = new window.V3InteractiveOverlay();
                window.v3InteractiveOverlay = overlay;
                console.log('✓ Created new overlay instance');
            } else {
                console.error('❌ V3InteractiveOverlay class not available');
                return false;
            }
        }
        
        if (overlay.start) {
            overlay.start();
            console.log('✓ Overlay started');
            return true;
        } else {
            console.error('❌ Overlay start method not available');
            return false;
        }
    } catch (error) {
        console.error('❌ Force start failed:', error);
        return false;
    }
};

// Reset function
window.v3Reset = function() {
    console.log('🔄 Resetting V3 Interactive Overlay...');
    
    try {
        // Remove existing UI elements
        const elementsToRemove = [
            '#v3-interactive-overlay',
            '#v3-toolbar', 
            '#v3-sidebar',
            '#v3-inspector',
            '#v3-fallback-toolbar'
        ];
        
        elementsToRemove.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.remove();
                console.log(`✓ Removed ${selector}`);
            }
        });
        
        // Clear highlights
        document.querySelectorAll('.v3-highlighted').forEach(el => {
            el.classList.remove('v3-highlighted');
            el.style.outline = '';
            el.style.backgroundColor = '';
        });
        
        // Remove labels
        document.querySelectorAll('.v3-element-label').forEach(label => {
            label.remove();
        });
        
        // Reset cursor
        document.body.style.cursor = '';
        
        // Clear instance
        window.v3InteractiveOverlay = null;
        
        console.log('✓ Reset complete');
        return true;
    } catch (error) {
        console.error('❌ Reset failed:', error);
        return false;
    }
};

// Fallback toolbar
window.v3Fallback = function() {
    console.log('🔧 Creating fallback toolbar...');
    
    // Remove existing fallback
    const existing = document.querySelector('#v3-fallback-toolbar');
    if (existing) existing.remove();
    
    const toolbar = document.createElement('div');
    toolbar.id = 'v3-fallback-toolbar';
    toolbar.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 999999;
        font-family: Arial, sans-serif;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid rgba(255,255,255,0.2);
    `;
    
    toolbar.innerHTML = `
        <div style="text-align: center;">
            <div style="font-weight: bold; margin-bottom: 4px;">🎯 V3 Interactive Scraper</div>
            <div style="font-size: 12px;">Fallback Mode - Click for options</div>
        </div>
    `;
    
    toolbar.onclick = function() {
        const options = [
            '1. Force start overlay: window.v3ForceStart()',
            '2. Reset everything: window.v3Reset()',
            '3. Debug report: window.v3Debug()',
            '4. Manual selection mode: Use browser dev tools',
            '5. Refresh page and try again'
        ].join('\\n\\n');
        
        alert(`V3 Interactive Scraper - Fallback Options\\n\\n${options}`);
    };
    
    document.body.appendChild(toolbar);
    console.log('✓ Fallback toolbar created');
    
    return toolbar;
};

// Error tracking
window.v3Errors = window.v3Errors || [];

// Error handler
window.addEventListener('error', function(event) {
    if (event.error && event.error.stack && event.error.stack.includes('V3')) {
        const errorMsg = `${event.error.message} at ${event.filename}:${event.lineno}`;
        window.v3Errors.push(errorMsg);
        console.error('V3 Error captured:', errorMsg);
    }
});

// Unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && typeof event.reason === 'string' && event.reason.includes('V3')) {
        window.v3Errors.push(`Unhandled promise: ${event.reason}`);
        console.error('V3 Promise rejection captured:', event.reason);
    }
});

console.log('🔧 V3 Debug Helper loaded');
console.log('💡 Use window.v3Debug() to diagnose issues');
console.log('🚀 Use window.v3ForceStart() to force start overlay');
console.log('🔄 Use window.v3Reset() to reset everything');
console.log('🔧 Use window.v3Fallback() for fallback toolbar');