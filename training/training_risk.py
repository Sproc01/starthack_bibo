from neural_network_drought import NN_drought
from neural_network_risk import NN_risk
import torch
import numpy as np
import torch.nn as nn

neural_network = NN_risk(1488, 3*12)
epochs = 100
learning_rate = 0.001
optimizer = torch.optim.Adam(neural_network.parameters(), lr=learning_rate)
criterion = nn.MSELoss()



batch_size = 128
input = data[:][0:2]
output = data[:][2]
for epoch in range(epochs):
  optimizer.zero_grad()
  for j in range(len(input), batch_size):
    x = input[j:j+batch_size]
    y = output[j:j+batch_size]
    x = torch.tensor(x, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32)
    x = x.reshape(-1)
    y_predicted = neural_network(x)
    avg_loss += criterion(y_predicted, y)
  avg_loss = avg_loss / batch_size
  if epoch % 10 == 0:
      print(f"Epochs:{epoch}, loss: {avg_loss}")
  avg_loss.backward()
  optimizer.step()