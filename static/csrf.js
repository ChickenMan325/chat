// CSRF token handling for Flask-JWT-Extended
function getCsrfToken() {
    const tokenCookieName = 'csrf_access_token'; // Default name in Flask-JWT-Extended
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === tokenCookieName) {
            return decodeURIComponent(value);
        }
    }
    return null;
}

// Add CSRF token to all fetch requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Only add token for same-origin requests that modify data
    if (typeof url === 'string' && 
        (url.startsWith('/') || url.startsWith(window.location.origin)) && 
        options.method && 
        ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
        
        // Get the CSRF token
        const token = getCsrfToken();
        
        if (token) {
            // Create headers if they don't exist
            if (!options.headers) {
                options.headers = {};
            }
            
            // If headers is a Headers object, use set method
            if (options.headers instanceof Headers) {
                options.headers.set('X-CSRF-TOKEN', token);
            } 
            // Otherwise treat as plain object
            else {
                options.headers['X-CSRF-TOKEN'] = token;
            }
        }
    }
    
    // Call original fetch with modified options
    return originalFetch(url, options);
};

console.log('CSRF protection initialized');
