import uuid

def generate_ref_code():
    code = 'http://127.0.0.1:8000/store/' + str(uuid.uuid4()).replace("-", "")[:12]
    return code