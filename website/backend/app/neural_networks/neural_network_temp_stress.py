import torch
import torch.nn as nn


class NN_temp_stress(nn.Module):
    def __init__(self, input_size, output_size, device):
        super(NN_temp_stress, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.ac1 = nn.ReLU()
        self.fc2 = nn.Linear(512, 256)
        self.ac2 = nn.ReLU()
        self.fc3 = nn.Linear(256, output_size)
        self.ac3 = nn.Sigmoid()
        self.device = device

    def forward(self, state):
        state.to(self.device)
        x = self.fc1(state)
        x = self.ac1(x)
        x = self.fc2(x)
        x = self.ac2(x)
        x = self.fc3(x)
        x = self.ac3(x)
        return x

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        torch.load_state_dict(torch.load(path))
