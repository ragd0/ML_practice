import torch
from torch.utils.data import Dataset, DataLoader

class AirDataset(Dataset):
    def __init__(self, data, targets):
        self.data = torch.tensor(data.values, dtype=torch.float32)
        self.targets = torch.tensor(targets.values, dtype=torch.float32)
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.targets[idx]