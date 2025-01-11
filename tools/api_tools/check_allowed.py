def check_is_allowed(filename: str, extension: list):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extension