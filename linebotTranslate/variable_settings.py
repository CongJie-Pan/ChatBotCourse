# Variable settings module for storing user language preferences
# This module provides simple get/set functionality for user language settings

# In-memory storage for user language settings
# In production, this should be replaced with a database solution
user_settings = {}

def get(user_id):
    """
    Get the language setting for a specific user.
    
    Args:
        user_id (str): The user ID to retrieve settings for
        
    Returns:
        str or None: The language code if found, None otherwise
    """
    return user_settings.get(user_id)

def set(user_id, language):
    """
    Set the language setting for a specific user.
    
    Args:
        user_id (str): The user ID to set settings for
        language (str): The language code to set (e.g., 'en', 'ja', 'zh')
    """
    user_settings[user_id] = language

def clear(user_id):
    """
    Clear the language setting for a specific user.
    
    Args:
        user_id (str): The user ID to clear settings for
    """
    if user_id in user_settings:
        del user_settings[user_id]

def get_all():
    """
    Get all user settings.
    
    Returns:
        dict: Dictionary of all user settings
    """
    return user_settings.copy() 