import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
import copy

# A 3 layer Feed Forward Neural Network
class QNet(nn.Module):
    def __init__(self, input_dim, action_space):
        super(QNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_space)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
    
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:

    def __init__(self, model, lr, gamma, target_update = 10):
        self.lr = lr
        self.model = model
        self.target_model = copy.deepcopy(model)
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.target_update = target_update
        self.update_counter = 0
        self.criterion = nn.MSELoss()

    def train_step(self, state : torch.Tensor, 
                   action, 
                   reward,
                   next_state : torch.Tensor, done):
        
        state = torch.tensor(state, dtype = torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype = torch.float)

        # If the shape is a single vector, reshape to batches
        if len(state.shape) == 1:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = (done, )

        pred = self.model(state)
        target = pred.clone()

        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                # Update the Q value using the Bellman Equation
                # Target Network predicts the Q value for all possible actions from the next state
                # If the Q network takes the same action as the target network action, then the loss will be low
                Q_new = reward[idx] + self.gamma * torch.max(self.target_model(next_state[idx]))

            # Update the target with the current Q value
            target[idx][action[idx].item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()


        # Update the target network
        self.update_counter += 1
        if self.update_counter % self.target_update == 0:
            self.target_model.load_state_dict(self.model.state_dict())
    
    # Manual Target Network Update
    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())

    





        
        



        

