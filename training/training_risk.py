from neural_network_drought import NN_drought
from neural_network_risk import NN_risk
import torch
import numpy as np
import torch.nn as nn
import meteoblue_data_adapter as mda

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

neural_network = NN_risk(1476, 36, device).to(device)
epochs = 100
learning_rate = 0.1
optimizer = torch.optim.SGD(neural_network.parameters(), lr=learning_rate)
criterion = nn.MSELoss()

res = list(mda.get_meteobluedata_with_risk_numpy('./stress_buster_data.db', 'SoyBean'))
historical = []
forecast = []
prediction = []
for i in range(len(res)):
    historical.append(res[i][0])
    forecast.append(res[i][1])
    prediction.append(res[i][2]/9)

batch_size = 128
for epoch in range(epochs):
    indices = np.random.permutation(len(historical))
    
    historical_shuffled = [historical[i] for i in indices]
    forecast_shuffled = [forecast[i] for i in indices]
    prediction_shuffled = [prediction[i] for i in indices]
    epoch_loss = 0
    num_batches = 0
    for j in range(0, len(historical_shuffled)-batch_size, batch_size):
        optimizer.zero_grad()

        x = historical_shuffled[j:j+batch_size]
        f = forecast_shuffled[j:j+batch_size]
        y = prediction_shuffled[j:j+batch_size]

        x = torch.tensor(np.array(x), dtype=torch.float32).to(device)
        f = torch.tensor(np.array(f), dtype=torch.float32).to(device)
        y = torch.tensor(np.array(y), dtype=torch.float32).to(device)

        x = x.reshape((batch_size, -1))
        f = f.reshape((batch_size, -1))
        x = torch.cat((x, f), 1).to(device)
        y = y.reshape((batch_size, 36))

        y_predicted = neural_network(x)
        epoch_loss += criterion(y_predicted, y)
        #loss.backward()
        #optimizer.step()
        num_batches += 1
        #epoch_loss += loss.item()
    avg_loss = epoch_loss / num_batches  
    avg_loss.backward()
    optimizer.step()
    epoch_loss /= num_batches
    if epoch % 10 == 0:
        print(f"Epochs:{epoch}, loss: {epoch_loss}")