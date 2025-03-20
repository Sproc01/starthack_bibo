from neural_network_drought import NN_drought
from neural_network_risk import NN_risk
import torch
import numpy as np
import torch.nn as nn

neural_network = NN_risk(1488, 3*12)
epochs = 10
learning_rate = 0.001
optimizer = torch.optim.Adam(neural_network.parameters(), lr=learning_rate)
criterion = nn.MSELoss()

for i in range(epochs):
    dataset = np.load('dataset.npy')
    X = dataset[:, :-3*12]
    y = dataset[:, -3*12:]
    optimizer.zero_grad()
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32)
    y_predicted = neural_network(X)
    loss = criterion(y_predicted, y)
    if i % 100 == 0:
        print(f"Epochs:{i}, loss: {loss}")
    loss.backward()
    optimizer.step()

neural_network = NN_drought(1460, 3*12)
epochs = 10
learning_rate = 0.001
optimizer = torch.optim.Adam(neural_network.parameters(), lr=learning_rate)
criterion = nn.MSELoss()

for i in range(epochs):
    dataset = np.load('dataset.npy')
    X = dataset[:, :-3*12]
    y = dataset[:, -3*12:]
    optimizer.zero_grad()
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32)
    y_predicted = neural_network(X)
    loss = criterion(y_predicted, y)
    if i % 100 == 0:
        print(f"Epochs:{i}, loss: {loss}")
    loss.backward()
    optimizer.step()