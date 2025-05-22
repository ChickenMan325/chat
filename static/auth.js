function checkAuthStatus() {
    fetch('/api/user/me', {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (window.location.pathname !== '/dashboard') {
                window.location.href = '/dashboard';
            }
            if (data.user && data.user.username) {
                registerWithSocket(data.user.username);
            }
        } else {
            if (window.location.pathname === '/dashboard') {
                window.location.href = '/login';
            }
        }
    })
    .catch(error => {
        console.error('Auth check error:', error);
        if (window.location.pathname === '/dashboard') {
            window.location.href = '/login';
        }
    });
}

function logout() {
    return fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
            'Accept': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/login';
        }
        return data;
    });
}

function clearAccessTokenCookie() {
    console.log('Clearing access_token_cookie');
    document.cookie = "access_token_cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    console.log('Access token cookie cleared');
}

let socket = null;
let registeredUsername = null;

function initSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            if (registeredUsername) {
                registerWithSocket(registeredUsername);
            }
        });
        
        socket.on('force_logout', function(data) {
            console.log('Force logout received:', data);
            
            clearAccessTokenCookie();
            let message = 'Your session has expired, please login again';
            if (data.reason === 'suspended') {
                message = data.message || 'Your account has been suspended';
            }
            
            console.log('Redirecting to login with message:', message);
            
            window.location.href = '/login?error=' + encodeURIComponent(message);
        });
        
        socket.on('test_event', function(data) {
            console.log('Test event received:', data);
            alert('Test event received: ' + JSON.stringify(data));
        });
    } else {
        console.error('Socket.IO not loaded - make sure the Socket.IO client script is included in your HTML');
    }
}

// Register user with socket when logged in
function registerWithSocket(username) {
    registeredUsername = username; // Store username for reconnection
    
    if (socket && socket.connected) {
        socket.emit('register_user', { username: username });
    } else {
        // Initialize socket if not already done
        if (!socket) {
            initSocket();
        }
        
        // Try again after a delay
        setTimeout(() => {
            if (socket && socket.connected) {
                socket.emit('register_user', { username: username });
            }
        }, 1000);
    }
}

// Test function to verify event reception
function testSocketEvent() {
    if (!registeredUsername) {
        console.error('No username registered with socket');
        return;
    }
    
    fetch('/api/test/emit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            username: registeredUsername,
            event: 'test_event',
            payload: { message: 'Test message from server' }
        }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Test emit result:', data);
    })
    .catch(error => {
        console.error('Test emit error:', error);
    });
}


// Initialize socket connection when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSocket();
    
    // Register with socket if we're on the dashboard
    if (window.location.pathname === '/dashboard') {
        fetch('/api/user/me', {
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.user && data.user.username) {
                registerWithSocket(data.user.username);
            }
        });
    }
});
