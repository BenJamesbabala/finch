import torch 
from torch import nn
from torch.autograd import Variable
import numpy as np


class RNNClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(RNNClassifier, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.build_model()
    # end constructor

    
    def forward(self, x):
        h0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size)) # set initial states  
        c0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size)) # set initial states 
        out, _ = self.lstm(x, (h0, c0)) # forward propagate
        out = self.fc(out[:, -1, :]) # decode hidden state of last time step
        return out
    # end method forward


    def build_model(self):
        self.lstm = nn.LSTM(self.input_size, self.hidden_size, self.num_layers, batch_first=True)
        self.fc = nn.Linear(self.hidden_size, self.num_classes)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
    # end method build_model


    def fit(self, X, y, num_epochs, batch_size):
        for epoch in range(num_epochs):
            i = 0
            for X_train_batch, y_train_batch in zip(self.gen_batch(X, batch_size),
                                                    self.gen_batch(y, batch_size)):
                images = Variable(torch.from_numpy(X_train_batch.astype(np.float32)))
                labels = Variable(torch.from_numpy(y_train_batch.astype(np.int64)))
                # forward + backward + optimize
                self.optimizer.zero_grad()
                outputs = self.forward(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                i+=1
                if (i+1) % 100 == 0:
                    print ('Epoch [%d/%d], Step [%d/%d], Loss: %.5f'
                           %(epoch+1, num_epochs, i+1, int(len(X)/batch_size), loss.data[0]))
    # end method fit


    def evaluate(self, X_test, y_test, batch_size):
        correct = 0
        total = 0
        for X_test_batch, y_test_batch in zip(self.gen_batch(X_test, batch_size),
                                              self.gen_batch(y_test, batch_size)):
            images = Variable(torch.from_numpy(X_test_batch.astype(np.float32)))
            labels = torch.from_numpy(y_test_batch.astype(np.int64))
            outputs = self.forward(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum()
        print('Test Accuracy of the model on the 10000 test images: %d %%' % (100 * correct / total)) 
    # end method evaluate


    def gen_batch(self, arr, batch_size):
        if len(arr) % batch_size != 0:
            new_len = len(arr) - len(arr) % batch_size
            for i in range(0, new_len, batch_size):
                yield arr[i : i + batch_size]
        else:
            for i in range(0, len(arr), batch_size):
                yield arr[i : i + batch_size]
    # end method gen_batch
# end class RNNClassifier