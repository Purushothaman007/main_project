import uuid

def generate_execution_id() -> str:
    """Generates a unique tracking execution ID in the format exec_<short_uuid>."""
    return f"exec_{uuid.uuid4().hex[:8]}"
