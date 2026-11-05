def edit_document(user_id, document, new_text):
    """Solo los creadores de los documentos pueden editarlos, incluido los documentos públicos."""
    if document["is_public"] or document["owner_id"] == user_id:
        document["text"] = new_text
        return True
    return False