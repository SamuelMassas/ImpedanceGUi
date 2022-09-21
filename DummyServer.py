from SC_interface import Server
import threading


# with open('socket_coms.txt', 'r') as file:
#    data = file.read()

data = b'[[1.00000e+05 1.39039e+02 5.92475e+00 1.39165e+02 2.44002e+00]\n [7.91230e+04 1.39469e+02 7.31748e+00 1.39661e+02 3.00336e+00]\n [6.26050e+04 1.39931e+02 8.89549e+00 1.40213e+02 3.63744e+00]\n [4.95350e+04 1.40650e+02 1.07672e+01 1.41061e+02 4.37764e+00]\n [3.91940e+04 1.41573e+02 1.29576e+01 1.42165e+02 5.22948e+00]\n [3.10120e+04 1.42618e+02 1.55385e+01 1.43462e+02 6.21794e+00]\n [2.45380e+04 1.43885e+02 1.85748e+01 1.45079e+02 7.35593e+00]\n [1.94150e+04 1.45551e+02 2.21921e+01 1.47233e+02 8.66910e+00]\n [1.53620e+04 1.47482e+02 2.64626e+01 1.49837e+02 1.01723e+01]\n [1.21550e+04 1.49722e+02 3.15148e+01 1.53003e+02 1.18866e+01]\n [9.61720e+03 1.52497e+02 3.75231e+01 1.57045e+02 1.38235e+01]\n [7.60950e+03 1.55741e+02 4.47016e+01 1.62030e+02 1.60148e+01]\n [6.02090e+03 1.59611e+02 5.32467e+01 1.68258e+02 1.84489e+01]\n [4.76390e+03 1.64620e+02 6.35433e+01 1.76458e+02 2.11066e+01]\n [3.76940e+03 1.70884e+02 7.58897e+01 1.86977e+02 2.39461e+01]\n [2.98250e+03 1.79166e+02 9.05775e+01 2.00760e+02 2.68189e+01]\n [2.35980e+03 1.90056e+02 1.07741e+02 2.18471e+02 2.95486e+01]\n [1.86720e+03 2.04699e+02 1.27293e+02 2.41050e+02 3.18757e+01]\n [1.47740e+03 2.24353e+02 1.48729e+02 2.69174e+02 3.35414e+01]\n [1.16900e+03 2.50100e+02 1.70759e+02 3.02834e+02 3.43238e+01]\n [9.24910e+02 2.82202e+02 1.91357e+02 3.40963e+02 3.41406e+01]\n [7.31820e+02 3.20630e+02 2.08388e+02 3.82399e+02 3.30211e+01]\n [5.79040e+02 3.63450e+02 2.19503e+02 4.24591e+02 3.11295e+01]\n [4.58160e+02 4.08305e+02 2.23506e+02 4.65476e+02 2.86963e+01]\n [3.62510e+02 4.51759e+02 2.20888e+02 5.02870e+02 2.60564e+01]\n [2.86830e+02 4.91259e+02 2.12976e+02 5.35438e+02 2.34382e+01]\n [2.26950e+02 5.25833e+02 2.01897e+02 5.63261e+02 2.10046e+01]\n [1.79570e+02 5.54840e+02 1.90756e+02 5.86715e+02 1.89731e+01]\n [1.42080e+02 5.79887e+02 1.81110e+02 6.07512e+02 1.73446e+01]\n [1.12420e+02 6.00857e+02 1.74045e+02 6.25556e+02 1.61543e+01]\n [8.89510e+01 6.20051e+02 1.70559e+02 6.43081e+02 1.53801e+01]\n [7.03810e+01 6.38190e+02 1.71185e+02 6.60750e+02 1.50153e+01]\n [5.56880e+01 6.56904e+02 1.75981e+02 6.80068e+02 1.49971e+01]\n [4.40620e+01 6.78763e+02 1.84814e+02 7.03474e+02 1.52313e+01]\n [3.48640e+01 7.00584e+02 1.97137e+02 7.27792e+02 1.57160e+01]\n [2.75850e+01 7.25694e+02 2.12053e+02 7.56041e+02 1.62887e+01]\n [2.18260e+01 7.53217e+02 2.28804e+02 7.87202e+02 1.68971e+01]\n [1.72700e+01 7.86460e+02 2.48278e+02 8.24719e+02 1.75204e+01]\n [1.36640e+01 8.20637e+02 2.68529e+02 8.63454e+02 1.81192e+01]\n [1.08120e+01 8.59097e+02 2.90363e+02 9.06840e+02 1.86745e+01]\n [8.55470e+00 8.99676e+02 3.13521e+02 9.52739e+02 1.92126e+01]\n [6.76880e+00 9.43388e+02 3.39009e+02 1.00245e+03 1.97661e+01]\n [5.35570e+00 9.88495e+02 3.66930e+02 1.05440e+03 2.03650e+01]\n [4.23760e+00 1.03747e+03 3.98642e+02 1.11142e+03 2.10190e+01]\n [3.35290e+00 1.08963e+03 4.34602e+02 1.17311e+03 2.17447e+01]\n [2.65290e+00 1.14580e+03 4.76112e+02 1.24078e+03 2.25642e+01]\n [2.09910e+00 1.20645e+03 5.22772e+02 1.31484e+03 2.34278e+01]\n [1.66090e+00 1.27397e+03 5.76745e+02 1.39844e+03 2.43569e+01]\n [1.31410e+00 1.34681e+03 6.37692e+02 1.49015e+03 2.53368e+01]\n [1.03980e+00 1.42778e+03 7.08410e+02 1.59386e+03 2.63889e+01]\n [8.22720e-01 1.51802e+03 7.86218e+02 1.70954e+03 2.73807e+01]\n [6.50970e-01 1.61719e+03 8.74701e+02 1.83859e+03 2.84079e+01]\n [5.15070e-01 1.73069e+03 9.76166e+02 1.98701e+03 2.94244e+01]\n [4.07540e-01 1.85190e+03 1.09204e+03 2.14990e+03 3.05272e+01]\n [3.22460e-01 1.99715e+03 1.21868e+03 2.33961e+03 3.13920e+01]\n [2.55140e-01 2.14879e+03 1.36726e+03 2.54690e+03 3.24682e+01]\n [2.01880e-01 2.32418e+03 1.52571e+03 2.78022e+03 3.32829e+01]\n [1.59730e-01 2.52681e+03 1.71138e+03 3.05182e+03 3.41094e+01]\n [1.26380e-01 2.76062e+03 1.89227e+03 3.34690e+03 3.44287e+01]\n [1.00000e-01 2.99255e+03 2.11428e+03 3.66409e+03 3.52418e+01]]'

server = Server()
server.set_online()
threading.Thread(target=server.start_listening).start()
print('[SERVER] Waiting')
while not server.clients:  # waiting for clients
    pass
print('[SERVER] Sending data')
while True:
    input('Enter something: ')
    server.stream2client(server.clients[0], data)
