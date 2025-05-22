/**
 * Profile Settings JavaScript
 * Handles tab switching, form submission, and password strength meter
 */

// Flash message functions
function showFlash(message, type) {
    const flashElement = document.getElementById('flash-message');
    const flashIcon = document.getElementById('flash-icon');
    const flashContent = document.getElementById('flash-content');
    
    // Set content and type
    flashContent.textContent = message;
    
    if (type === 'error') {
        flashElement.className = 'flash-message flash-error show';
        flashIcon.className = 'fas fa-exclamation-circle';
    } else {
        flashElement.className = 'flash-message flash-success show';
        flashIcon.className = 'fas fa-check-circle';
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeFlash();
    }, 5000);
}

function closeFlash() {
    const flashElement = document.getElementById('flash-message');
    flashElement.classList.remove('show');
}

// Load user data from API
function loadUserData() {
    fetch('/api/user/me', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.user) {
            // Update username displays
            const usernameDisplays = document.querySelectorAll('.current-username');
            usernameDisplays.forEach(display => {
                display.textContent = data.user.username;
            });
            
            // Update profile picture if available
            const profilePicturePreview = document.getElementById('current-profile-picture');
            if (profilePicturePreview) {
                if (data.user.profile_picture) {
                    // Add timestamp to prevent caching
                    const timestamp = new Date().getTime();
                    profilePicturePreview.innerHTML = `<img src="/static/${data.user.profile_picture}?t=${timestamp}" alt="Profile Picture">`;
                } else {
                    profilePicturePreview.innerHTML = '<i class="fas fa-user"></i>';
                }
            }
        }
    })
    .catch(error => {
        console.error('Error loading user data:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Load user data when page loads
    loadUserData();
    
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Password visibility toggle
    const toggleBtns = document.querySelectorAll('.toggle-password');
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Profile picture preview
    const profilePictureInput = document.getElementById('profile-picture');
    const profilePicturePreview = document.getElementById('current-profile-picture');
    
    if (profilePictureInput && profilePicturePreview) {
        profilePictureInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Replace the content with the new image
                    profilePicturePreview.innerHTML = `<img src="${e.target.result}" alt="Profile Picture">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Profile picture form submission
    const profilePictureForm = document.getElementById('profile-picture-form');
    
    if (profilePictureForm) {
        profilePictureForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const profilePicture = document.getElementById('profile-picture').files[0];
            if (!profilePicture) {
                showFlash('Please select an image file', 'error');
                return;
            }
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Disable button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            
            // Create form data
            const formData = new FormData();
            formData.append('profile_picture', profilePicture);
            
            // Send request to server
            fetch('/api/user/update-profile-picture', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Show flash message
                    showFlash('Profile picture updated successfully!', 'success');
                    
                    // Reset form
                    profilePictureForm.reset();
                    
                    // Update the profile picture in the header if it exists
                    const headerProfilePic = document.querySelector('.header-profile-pic');
                    if (headerProfilePic) {
                        headerProfilePic.src = data.profile_picture;
                    }
                    
                    // Force reload the current profile picture to avoid caching
                    const timestamp = new Date().getTime();
                    const imgSrc = `/static/${data.profile_picture}?t=${timestamp}`;
                    profilePicturePreview.innerHTML = `<img src="${imgSrc}" alt="Profile Picture">`;
                    
                    // Reload user data to ensure everything is up to date
                    loadUserData();
                } else {
                    // Show flash message with error
                    showFlash(data.message || 'Failed to update profile picture', 'error');
                }
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            })
            .catch(error => {
                console.error('Error:', error);
                showFlash('An error occurred. Please try again.', 'error');
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }
    
    // Password strength meter
    const newPasswordInput = document.getElementById('new-password');
    const strengthBar = document.querySelector('.strength-bar');
    const passwordHint = document.querySelector('.password-hint');
    
    if (newPasswordInput && strengthBar) {
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let message = '';
            
            if (password.length >= 6) {
                strength += 20;
            }
            
            if (password.length >= 8) {
                strength += 20;
            }
            
            if (password.match(/[a-z]/)) {
                strength += 20;
            }
            
            if (password.match(/[A-Z]/)) {
                strength += 20;
            }
            
            if (password.match(/[0-9]/)) {
                strength += 20;
            }
            
            if (password.match(/[^a-zA-Z0-9]/)) {
                strength += 20;
            }
            
            // Cap at 100%
            strength = Math.min(strength, 100);
            
            // Update strength bar
            strengthBar.style.width = strength + '%';
            
            // Set color based on strength
            if (strength < 40) {
                strengthBar.style.backgroundColor = '#dc3545'; // Red
                message = 'Weak password';
            } else if (strength < 70) {
                strengthBar.style.backgroundColor = '#ffc107'; // Yellow
                message = 'Moderate password';
            } else {
                strengthBar.style.backgroundColor = '#28a745'; // Green
                message = 'Strong password';
            }
            
            // Update hint message
            if (password.length === 0) {
                passwordHint.textContent = 'Password must be at least 6 characters';
            } else {
                passwordHint.textContent = message;
            }
        });
    }
    
    // Username form submission
    const usernameForm = document.getElementById('username-form');
    
    if (usernameForm) {
        usernameForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const newUsername = document.getElementById('new-username').value;
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Disable button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            
            // Send request to server
            fetch('/api/user/update-username', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    new_username: newUsername
                }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show flash message
                    showFlash('Username updated successfully!', 'success');
                    
                    // Reset form
                    usernameForm.reset();
                    
                    // Update any username displays on the page if needed
                    const usernameDisplays = document.querySelectorAll('.current-username');
                    usernameDisplays.forEach(display => {
                        display.textContent = data.new_username;
                    });
                    
                    // Reload user data to ensure everything is up to date
                    loadUserData();
                } else {
                    // Show flash message with error
                    showFlash(data.message || 'Failed to update username', 'error');
                }
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            })
            .catch(error => {
                console.error('Error:', error);
                showFlash('An error occurred. Please try again.', 'error');
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }
    
    // Password form submission
    const passwordForm = document.getElementById('password-form');
    
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Check if passwords match
            if (newPassword !== confirmPassword) {
                showFlash('New passwords do not match', 'error');
                return;
            }
            
            // Disable button and show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            
            // Send request to server
            fetch('/api/password/change', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show flash message
                    showFlash('Password updated successfully!', 'success');
                    
                    // Reset form
                    passwordForm.reset();
                    
                    // Reset strength bar
                    if (strengthBar) {
                        strengthBar.style.width = '0%';
                        passwordHint.textContent = 'Password must be at least 6 characters';
                    }
                } else {
                    // Show flash message with error
                    showFlash(data.message || 'Failed to update password', 'error');
                }
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            })
            .catch(error => {
                console.error('Error:', error);
                showFlash('An error occurred. Please try again.', 'error');
                
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }
});
