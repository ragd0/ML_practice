import pandas as pd
import numpy as np
from model import Net
from mydataset import AirDataset
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


if __name__ == "__main__":
    data = pd.read_pickle("data/df_list27.pkl")
    
    #特徴量
    X = pd.concat(data, ignore_index=True).iloc[:, :59]
    y = pd.concat(data, ignore_index=True).iloc[:, 59:]
    
    print(X.shape)
    print(y.shape)
    
    
    #特徴量
    # X = data[0].iloc[:, :59]
    #予測対象
    # y = data[0].iloc[:, 59:]
    
    
    
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0, shuffle=False) 
    
    #標準化
    data_scaler = StandardScaler()
    target_scaler = StandardScaler()
    
    # X_train = data_scaler.fit_transform(X_train.values)
    # X_test = data_scaler.transform(X_test.values)
    
    # y_train = target_scaler.fit_transform(y_train.values)
    # y_test = target_scaler.transform(y_test.values)
       
    #データセットとデータローダー
    train_dataset = AirDataset(X_train, y_train)
    test_dataset = AirDataset(X_test, y_test)
    train_dataloader = DataLoader(train_dataset, batch_size=64, shuffle=False)
    test_dataloader = DataLoader(test_dataset, batch_size=64, shuffle=False)
    
    #モデル
    model = Net()
    #損失関数
    criterion = nn.MSELoss()
    #optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.1)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.8)
    
    num_epoch = 10
    for epoch in range(num_epoch):
        running_loss = 0.0
        for train_batch_idx, (train_batch_data, train_batch_targets) in enumerate(train_dataloader):
            optimizer.zero_grad()
            
            outputs = model(train_batch_data)
            loss = criterion(outputs, train_batch_targets)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()

            if train_batch_idx % 1000 == 999:    # 2,000ミニバッチにつき1度表示
                print('[%d, %5d] loss: %.3f' %
                    (epoch + 1, train_batch_idx + 1, running_loss / 1000))
                running_loss = 0.0
        scheduler.step()
        
    
    test_loss = []
    with torch.no_grad():
         for test_batch_idx, (test_batch_data, test_batch_targets) in enumerate(test_dataloader):
             outputs = model(test_batch_data)
             
            #  outputs_original = target_scaler.inverse_transform(outputs.numpy())
            #  targets_original = target_scaler.inverse_transform(test_batch_targets.numpy())
            #  print(outputs_original.shape, targets_original.shape)
            #  loss = criterion(outputs_original, targets_original)
             loss = criterion(outputs, test_batch_targets)
             test_loss.append(loss.item())
             

    print("テスト誤差: ", sum(test_loss) / len(test_loss))