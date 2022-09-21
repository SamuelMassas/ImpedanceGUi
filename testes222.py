import json
import numpy as np
arr = np.array([1, 2, 3, 4, 5])

data = {'name': 'my name', 'data': np.ndarray.tolist(arr)}

js_str = json.dumps(data)

print(js_str)


