try:
    from docmerge.config_custom import install_name, install_display, gdrive_root, local_root, email_credentials, email_default_recipient, remote_library, extend_path, library_page, compose_page
except:
    from .config_default import install_name, install_display, gdrive_root, local_root, email_credentials, email_default_recipient, remote_library, extend_path, library_page, compose_page

