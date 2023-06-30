import hashlib
import json
import time

def get_hash(message: str):
    """Return sha256 of the given message"""
    return hashlib.sha256(message.encode()).hexdigest()


def compute_hash(x: list):
    """Compute the hash of a list of elements
        --> prev_hash: [S, X, Y]
        --> state: [X, Y]
    """
    message = ""
    for i in x:
        if isinstance(i, list):
            if len(i) > 0 and hasattr(i[0], 'value'):
                message += json.dumps([trans.value for trans in i], sort_keys=True)
        elif isinstance(i, int):
            # message += json.dumps([str(i)], sort_keys=True)
            message += str(i)
        else:
            message += i
        dd = get_hash(message)
        # print(f">> Hash: {get_hash(message)} ---> {message}")
    return dd


    def start_timer():
        t = time.time()

if __name__ == '__main__':
    x = [1, 2, 3]
    s = "hello"
    y = "world"
    # print(compute_hash([compute_hash([s, x]), y]))
    # print(compute_hash([s, x]))
    print(compute_hash(['10b04e9746617bd9682fbc64239e3a7671a36d84b0dbafd079311b0ff91d2d0d','422952af8fc74e34b99c34dc11890be41fe5ac355d95cb79d2b3922e8ce40e88']))
    # print(compute_hash(["0"])) fd141a24b94ff9c021336844220bf0dd8a331a65d8fffc943eec45e2ec86b487
