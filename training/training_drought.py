from neural_network_drought import NN_drought
import torch
import numpy as np
import torch.nn as nn
from meteoblue_data_adapter import get_last30_days_sum

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
neural_network = NN_drought(8, 12, device)
epochs = 1000
learning_rate = 0.1
optimizer = torch.optim.SGD(neural_network.parameters(), lr=learning_rate)
criterion = nn.MSELoss()

data = get_last30_days_sum('./dataset/stress_buster_data.db')

sum_evaporation_past = []
sum_rainfall_past = []
sum_soil_moisture_past = []
sum_temp_past = []
sum_evaporation_present = []
sum_rainfall_present = []
sum_soil_moisture_present = []
sum_temp_present = []
output = []
for i in range(int(0.7*len(data[0]))):
  sum_evaporation_past.append(data[0][i])
  sum_rainfall_past.append(data[1][i])
  sum_soil_moisture_past.append(data[2][i])
  sum_temp_past.append(data[3][i])
  sum_evaporation_present.append(data[4][i])
  sum_rainfall_present.append(data[5][i])
  sum_soil_moisture_present.append(data[6][i])
  sum_temp_present.append(data[7][i])
  output.append(data[8][i])


batch_size = 256
for epoch in range(epochs):
  indices = np.random.permutation(len(sum_evaporation_past))
    
  sum_evaporation_past_shuffled = [sum_evaporation_past[i] for i in indices]
  sum_rainfall_past_shuffled = [sum_rainfall_past[i] for i in indices]
  sum_soil_moisture_past_shuffled = [sum_soil_moisture_past[i] for i in indices]
  temp_past_shuffled = [sum_temp_past[i] for i in indices]
  sum_evaporation_present_shuffled = [sum_evaporation_present[i] for i in indices]
  sum_rainfall_present_shuffled = [sum_rainfall_present[i] for i in indices]
  sum_soil_moisture_present_shuffled = [sum_soil_moisture_present[i] for i in indices]
  sum_temp_present_shuffled = [sum_temp_present[i] for i in indices]
  output_shuffled = [output[i] for i in indices]
  epoch_loss = 0
  num_batches = 0
  for j in range(0, len(sum_evaporation_past_shuffled)-batch_size, batch_size):
    optimizer.zero_grad()

    e_past = sum_evaporation_past_shuffled[j:j+batch_size]
    r_past = sum_rainfall_past_shuffled[j:j+batch_size]
    s_past = sum_soil_moisture_past_shuffled[j:j+batch_size]
    t_past = temp_past_shuffled[j:j+batch_size]
    e_present = sum_evaporation_present_shuffled[j:j+batch_size]
    r_present = sum_rainfall_present_shuffled[j:j+batch_size]
    s_present = sum_soil_moisture_present_shuffled[j:j+batch_size]
    t_present = sum_temp_present_shuffled[j:j+batch_size]

    y = output_shuffled[j:j+batch_size]

    x = torch.tensor(np.array([e_past, r_past, s_past, t_past, e_present, r_present, s_present, t_present]), dtype=torch.float32).to(device)
    y = torch.tensor(np.array(y), dtype=torch.float32).to(device)
    x = x.reshape((batch_size, -1))
    y = y.reshape((batch_size, 12))

    y_predicted = neural_network(x)
    loss = criterion(y_predicted, y)
    loss.backward()
    optimizer.step()
    num_batches += 1
    epoch_loss += loss.item()
  epoch_loss /= num_batches
  if epoch % 10==0:
    print(f"Epochs:{epoch}, loss: {epoch_loss}")

# test
test_loss = 0
sum_evaporation_past = []
sum_rainfall_past = []
sum_soil_moisture_past = []
sum_temp_past = []
sum_evaporation_present = []
sum_rainfall_present = []
sum_soil_moisture_present = []
sum_temp_present = []
output = []
for i in range(int(0.7*len(data[0])), len(data[0])):
  sum_evaporation_past.append(data[0][i])
  sum_rainfall_past.append(data[1][i])
  sum_soil_moisture_past.append(data[2][i])
  sum_temp_past.append(data[3][i])
  sum_evaporation_present.append(data[4][i])
  sum_rainfall_present.append(data[5][i])
  sum_soil_moisture_present.append(data[6][i])
  sum_temp_present.append(data[7][i])
  output.append(data[8][i])

for j in range(0, len(sum_evaporation_past)):
    e_past = sum_evaporation_past[j]
    r_past = sum_rainfall_past[j]
    s_past = sum_soil_moisture_past[j]
    t_past = sum_temp_past[j]
    e_present = sum_evaporation_present[j]
    r_present = sum_rainfall_present[j]
    s_present = sum_soil_moisture_present[j]
    t_present = sum_temp_present[j]

    y = output[j]

    x = torch.tensor(np.array([e_past, r_past, s_past, t_past, e_present, r_present, s_present, t_present]), dtype=torch.float32)
    y = torch.tensor(np.array(y), dtype=torch.float32)
    x = x.reshape((1, -1))
    y = y.reshape((1, 12))
    y_predicted = neural_network(x)
    loss = criterion(y_predicted, y)
    num_batches += 1
    test_loss += loss.item()
test_loss /= num_batches
print(f"Avg loss: {test_loss}")

neural_network.save('risk_model_drought.pth')


