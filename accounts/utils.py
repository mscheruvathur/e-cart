import uuid

def generate_ref_code():
    code = 'http://ec2-18-222-163-8.us-east-2.compute.amazonaws.com/store/' + str(uuid.uuid4()).replace("-", "")[:12]
    return code