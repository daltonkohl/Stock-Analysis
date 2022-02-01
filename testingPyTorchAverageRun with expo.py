"""
Title: Stock Net.py

Authors: 
Dalton Kohl - dalton.kohl@outlook.com
Liam Sefton - lsefton@sandiego.edu
Giacomo Radaelli - gradaelli@sandiego.edu

Date Last Modified: 02/01/2022

A single trianging and testing run of the Stock Analysis Neural Network

The net is trained to predict a 10% increase of stock price year to year using the PyTorch Library.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.modules.loss import MSELoss
import torch.optim as optim
import matplotlib.pyplot as plt


class ExampleNet(nn.Module):
    def __init__(self):
        super(ExampleNet, self).__init__()
        #This creates the layers
        self.linear_relu_stack = nn.Sequential( 
            nn.Linear(19, 15),
            nn.Tanh(),
            nn.Linear(15, 10),
            nn.Tanh(),
            nn.Linear(10, 5),
            nn.Tanh(),
            nn.Linear(5, 1)
        )

    def forward(self, x):
        #forward function must be defined, so we give it the layers we created above
        return self.linear_relu_stack(x)

#this function is used to initialize the weights to a set value to reduce randomness
line_num = 1
def init_weights(layer):
    if type(layer) == nn.Linear:
        layer.weight.data.fill_(0.0)
        layer.bias.data.fill_(1.0)

sum_of_runs = 0
num_of_counted_runs = 0




model = ExampleNet()
#model.apply(init_weights)
num_epochs = 5000
optimizer = optim.Adam(model.parameters(), lr=.000005) #learning rates higher than this tend to converge to local minima after first epoch
testing_differences = -1
curr_epoch = 0

#variables for pyplots
testing_error_y_vals = []
training_error_y_vals = []
x_vals_training = []
x_vals_testing = []

convergence_counter = 0
divergence_counter = 0

plt.xlim(1, 50)
plt.ylim(0, .5)
plt.title("Error on validation set")
plt.xlabel("Epochs")
plt.ylabel("Average error on samples")


#Training
for outer_loop in range(num_epochs):
    if outer_loop % 10 == 0:
        #for group in optimizer.param_groups:
        #    group['lr'] = group['lr'] - (group['lr']/10) #lowers weights slowly over time
        print(outer_loop)
    #for group in optimizer.param_groups:
    #    group['lr'] = group['lr'] - (group['lr']/100)
    f = open("training.txt", "r")
    sum_correct = 0
    num_samples = 0
    line_num = 1
    for line in f:
        line = line.split(",")
        line = list(map(float, line))
        target = [line[-1]] #target must be in list in order to be converted to tensor
        target = torch.FloatTensor(target)
        line = line[:-1]
        #output = model(torch.nan_to_num(torch.FloatTensor(line)))
        output = model(torch.FloatTensor(line))
        #print(output)
        #print(torch.nan_to_num(output))
        optimizer.zero_grad()
        loss_func = nn.MSELoss() #maybe try cross entropy
        loss = loss_func(output, target)
        loss.backward()
        optimizer.step()
        sum_correct += abs(target - output)
        num_samples += 1
        line_num += 1
    f.close()

    training_error_y_vals.append(float(sum_correct)/num_samples)
    x_vals_training.append(curr_epoch)

    #Overfitting prevention here
    divergence_threshold = .00001 #if (new average error) - (prev average error) > divergence_threshold
    convergence_threshold = .00005 #if abs(new average error - prev average error) < convergence_threshold 
    f = open("testing.txt", "r")
    sum_correct = 0
    num_samples = 0
    for line in f:
        line = line.split(",")
        line = list(map(float, line))
        target = [line[-1]]
        target = torch.nan_to_num(torch.FloatTensor(target))
        line = line[:-1]
        #line = [float(i)/max(line) for i in line] 
        output = model(torch.nan_to_num(torch.FloatTensor(line)))
        sum_correct += abs(target - output)
        num_samples += 1

    f.close()
    exit_code = -1
    #checking for convergence and divergence
    if testing_differences == -1: #if it is first iteration
        testing_differences = float(sum_correct)/num_samples
    elif float(sum_correct)/num_samples <= testing_differences: 
        divergence_counter = 0
        if abs(testing_differences - float(sum_correct)/num_samples) < convergence_threshold:
            convergence_counter += 1
            if convergence_counter == 10:
                exit_code = 0
                break
        else:
            convergence_counter = 0
            testing_differences = float(sum_correct)/num_samples
    else:
        if float(sum_correct)/num_samples - testing_differences > divergence_threshold:
            divergence_counter += 1
            if divergence_counter == 5:
                exit_code = 1
                break
        else:
            divergence_counter = 0

    curr_epoch += 1
    line_num += 1

    testing_error_y_vals.append(float(sum_correct)/num_samples)
    x_vals_testing.append(curr_epoch)



    ylim_multiplier = 2
    if(max(x_vals_testing) > 39):
        plt.xlim(1, max(x_vals_testing) + curr_epoch*.75)
    if(float(sum_correct)/num_samples >= .8):
        plt.ylim(0,float(sum_correct)/num_samples * ylim_multiplier)
    elif(float(sum_correct)/num_samples < .8):
        plt.ylim(float(sum_correct)/num_samples * float(sum_correct)/num_samples,.5)
    plt.plot(x_vals_testing, testing_error_y_vals)
    ylim_multiplier -= .01
    plt.pause(.01)


if exit_code == -1:
    print("Training stopped after " + str(curr_epoch) + " epochs from reaching max epochs.")
elif exit_code == 0:
    print("Training stopped after " + str(curr_epoch) + " epochs from achieving convergence.")
elif exit_code == 1:
    print("Training stopped after " + str(curr_epoch) + " epochs from overfitting prevention.")

if curr_epoch > 99:
    num_of_counted_runs += 1


#Testing
f = open("binarytesting.txt", "r")
sum_correct = 0
num_samples = 0
for line in f:
    line = line.split(",")
    line = list(map(float, line))
    target = [line[-1]]
    target = torch.nan_to_num(torch.FloatTensor(target))
    line = line[:-1]
    #line = [float(i)/max(line) for i in line] #this does normalization
    output = model(torch.nan_to_num(torch.FloatTensor(line)))
    #print(output)
    if float(output) > .1:
        if float(target) == 1:
            sum_correct += 1
        num_samples += 1
    
print("Testing result: ", end="")
if num_samples > 0:
    print(float(sum_correct)/num_samples)
    if curr_epoch > 99:
        sum_of_runs += float(sum_correct)/num_samples

        
else:
    print("0.0")
    if curr_epoch > 99:
        sum_of_runs += 0.0



#Look at this graph

#plt.show()
plt.close()
plt.plot(x_vals_testing, testing_error_y_vals)
plt.savefig("testing_differences_by_epoch.png")
plt.close()
plt.plot(x_vals_training, training_error_y_vals)
plt.savefig("training_differences_by_epoch.png")
f.close()


