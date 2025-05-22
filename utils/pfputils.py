import os
import uuid
from utils.config import Config
from utils.logutils import log_info, log_error

def allowed_file(filename):
    """
    Check if a file has an allowed extension
    
    Args:
        filename: Name of the file to check
        
    Returns:
        Boolean indicating if the file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_profile_picture(file):
    """
    Save a profile picture to the configured directory
    
    Args:
        file: File object from request.files
        
    Returns:
        Filename of saved image or None if failed
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        filename = str(uuid.uuid4().hex) + '_' + os.path.basename(file.filename)
        file_path = os.path.join(Config.PROFILE_PICTURES_DIR, filename)
        
        os.makedirs(Config.PROFILE_PICTURES_DIR, exist_ok=True)
        file.save(file_path)
        
        log_info(f"Profile picture saved: {filename}")
        return filename
    except Exception as e:
        log_error(f"Error saving profile picture: {str(e)}")
        return None

def delete_profile_picture(filename):
    """
    Delete a profile picture from the configured directory
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Boolean indicating success or failure
    """
    if not filename:
        return False
    
    try:
        file_path = os.path.join(Config.PROFILE_PICTURES_DIR, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            log_info(f"Deleted profile picture: {filename}")
            return True
        
        return False
    except Exception as e:
        log_error(f"Error deleting profile picture: {str(e)}")
        return False
