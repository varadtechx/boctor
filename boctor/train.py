import json
import os 
from boctor.utils import dataloader
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from boctor.model import NeuralNet




def train(filepath,epochs,learning_rate,model_dir):
    X_train,y_train,all_words,tags = dataloader(filepath)
    y_train = np.array(y_train)

    class ChatDataset(Dataset):
        def __init__(self):
            self.n_samples = len(X_train)
            self.x_data = X_train
            self.y_data = y_train

        def __getitem__(self,index):
            return self.x_data[index],self.y_data[index]

        def __len__(self):
            return self.n_samples

    # Hyperparameters
    batch_size = 8
    hidden_size = 8
    output_size = len(tags)
    input_size = len(X_train[0])
    # learning_rate = learning_rate
    num_epochs = epochs

    dataset = ChatDataset()
    train_loader = DataLoader(dataset=dataset, batch_size=batch_size,shuffle=True,num_workers=0)


    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = NeuralNet(input_size, hidden_size, output_size).to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Train the model
    for epoch in range(num_epochs):
        for (words, labels) in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)

            #forward
            outputs = model(words)
            loss = criterion(outputs,labels)

            #backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch+1)%10 == 0:
            print(f'epoch {epoch+1}/{num_epochs},loss={loss.item():.4f}')


            # Forward pass
            outputs = model(words)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    print(f'final loss : , loss={loss.item():.4f}')


    data = { 
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "tags": tags
    }
    
    FILE = os.path.join(model_dir,"model.pth")
    torch.save(data, FILE)

    print(f'Training complete. Model saved to {FILE}')

    return model





