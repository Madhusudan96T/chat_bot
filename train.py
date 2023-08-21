from nltk_utils import tokenize,stem,bag_of_words
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset,DataLoader
from model import NeuralNet

with open("intents.json",'r') as f:
    intents=json.load(f)

all_words=[]
tags=[]
XY=[]
for intent in intents['intents']:
    tag=intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w=tokenize(pattern)
        all_words.extend(w)
        XY.append((w,tag))

ignore_words=['?','!','.',',']

all_words=[stem(w) for w in all_words if w not in ignore_words]
all_words=sorted(set(all_words))
tag=sorted(set(tags))

X_train=[] 
y_train=[]
for (pattern_sentence,tag) in XY:
    bag=bag_of_words(pattern_sentence,all_words)
    X_train.append(bag)
    label=tags.index(tag)
    y_train.append(label)

X_train=np.array(X_train)
y_train=np.array(y_train)

class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples=len(X_train)
        self.x_data = torch.tensor(X_train, dtype=torch.float32)  # Convert to torch tensor
        self.y_data = torch.tensor(y_train, dtype=torch.long)     # Convert to torch tensor
    def __getitem__(self,index):
        return self.x_data[index],self.y_data[index]
    def __len__(self):
        return self.n_samples

#hyperparam
batch_size=8
hidden_size=8
output_size=len(tags)
input_size=len(all_words) #or u could use len of all words
learning_rate=.001
num_epochs=1000


dataset=ChatDataset()
train_loader=DataLoader(dataset=dataset,batch_size=batch_size,shuffle=True,num_workers=0)    

device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model=NeuralNet(input_size,hidden_size,output_size).to(device)

#loss and optimizer
criterion=nn.CrossEntropyLoss()
optimizer=torch.optim.Adam(model.parameters(),lr=learning_rate)

for epoch in range(num_epochs):
    for (words,labels) in train_loader:
        words=words.to(device)
        labels=labels.to(device)

        #forward
        outputs=model(words)
        loss=criterion(outputs,labels)

        #backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    if (epoch+1)%100==0:
        print(f'epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}')
print(f'final loss: {loss.item():.4f}')