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
        x = torch.clamp(x, 0, 9)
        return x
    
    def save(self, path):
        '''Save the model'''
        torch.save(self.state_dict(), path)
    
    def load(self, path):
        torch.load_state_dict(torch.load(path))


