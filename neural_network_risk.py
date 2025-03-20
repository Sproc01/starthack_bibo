import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class NN_risk(nn.Module):
    def __init__(self, input_size, output_size):
        '''Creates the model'''
        super(NN_risk, self).__init__()
        self.fc1 = nn.Linear(input_size, 2000)
        self.ac1 = nn.SiLU()
        self.fc2 = nn.Linear(2000, 1000)
        self.ac2 = nn.SiLU()
        self.fc3 = nn.Linear(1000, output_size)

    def forward(self, state):
        '''Do the prediction given the input'''
        x = self.fc1(state)
        x = self.ac1(x)
        x = self.fc2(x)
        x = self.ac2(x)
        x = self.fc3(x)
        return x
    
    def save(self, path):
        '''Save the model'''
        torch.save(self.state_dict(), path)
    
    def load(self, path):
        torch.load_state_dict(torch.load(path))


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