import subprocess

def vipe(text):
    cmd = f"echo '{text}' | vipe"
    output = subprocess.check_output(cmd, shell=True)
    return output.decode()
