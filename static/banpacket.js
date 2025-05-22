function banUser(userId) {
    console.log('Attempting to ban user:', userId);
    return fetch('/api/admin/ban', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ user_id: userId }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ban result:', data);
        return data;
    })
    .catch(error => {
        console.error('Ban error:', error);
        throw error;
    });
}

function unbanUser(userId) {
    console.log('Attempting to unban user:', userId);
    return fetch('/api/admin/unban', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ user_id: userId }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Unban result:', data);
        return data;
    })
    .catch(error => {
        console.error('Unban error:', error);
        throw error;
    });
}

function forceLogout(userId) {
    return fetch('/api/auth/force-logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ user_id: userId }),
        credentials: 'include'
    })
    .then(response => response.json());
}

window.banUser = banUser;
window.unbanUser = unbanUser;
window.forceLogout = forceLogout;