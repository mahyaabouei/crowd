import random
import string

def generate_token () : 
    generated_token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
    return generated_token



