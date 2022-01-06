import argparse
import os
import shutil
from random import randint, random, sample

import cv2
import numpy as np
import torch
import torch.nn as nn
from tensorboardX import SummaryWriter

from deep_q_learning import DeepQNetwork
from flappy_qlearning import Flappy


def process_image(image, width, height):
    image = cv2.cvtColor(cv2.resize(image, (width, height), cv2.COLOR_BGR2GRAY))
    x, image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
    return image[None, :, :].astype(np.float32)

def find_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--batch_size", type=int, default=64, help="The number of images per batch")
    parser.add_argument("--image-size", type=int, default=84)
    parser.add_argument("--group-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-6)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--initial_epsilon", type=float, default=0.1)
    parser.add_argument("--final_epsilon", type=float, default=1e-4)
    parser.add_argument("--num_iters", type=int, default=2000000)
    parser.add_argument("--replay_size", type=int, default=50000,
                        help="Number of epoches between testing phases")
    parser.add_argument("--log-path", type=str, default="tensorboard")
    parser.add_argument("--saved-path", type=str, default="models")

    return parser.parse_args()

def train(opt):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    model = DeepQNetwork()
    if os.path.isdir(opt.log_path):
        shutil.rmtree(opt.log_path)
    os.makedirs(opt.log_path)
    write = SummaryWriter(opt.log_path)
    optimize = torch.optim.Adam(model.parameters(), lr=opt.lr)
    criteria = nn.MSELoss()
    gamestate = Flappy()
    image, reward, terminal = gamestate.next_frame(0)
    if torch.cuda.is_available():
        model.cuda()
        image = image.cuda()
    state = torch.cat(tuple(image for _ in range(4)))[None, :, :, :]

    replay = []
    i = 0
    while i < opt.num_iters:
        pred = model(state)[0]
        epsilon = opt.final_epsilon + ((opt.num_iters - i) * (opt.initial_epsilon - opt.final_epsilon) / opt.num_iters)
        u = random()
        if u <= epsilon:
            action = randint(0, 1)
        else:
            action = torch.argmax(pred).item()

        next_image, reward, terminal = gamestate.next_frame(action)
        if torch.cuda.is_available():
            next_image = next_image.cuda()
        next_state = torch.cat((state[0, 1:, :, :], next_image))[None, :, :, :]
        replay.append([state, action, reward, next_state, terminal])
        if len(replay) > opt.replay_size:
            del replay[0]

        batch = sample(replay, min(len(replay), opt.batch_size))
        state_batch, action_batch, reward_batch, next_state_batch, terminal_batch = zip(*batch)
        state_batch = torch.cat(tuple(state for state in state_batch))
        action_batch = torch.from_numpy(np.array([[1, 0] if action == 0 else [0, 1] for action in action_batch], dtype=np.float32))
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.cat(tuple(state for state in next_state_batch))
        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            action_batch = action_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()
        current_prediction_batch = model(state_batch)
        next_prediction_batch = model(next_state_batch)
        
        y_batch = torch.cat(tuple(reward if done else reward + opt.gamma * torch.max(prediction) for reward, done, prediction in zip(reward_batch, terminal_batch, next_prediction_batch)))
        # y_batch = torch.cat(tuple(reward if terminal else reward + opt.gamma * torch.max(prediction) for reward, terminal, prediction in zip(reward_batch, terminal_batch, next_prediction_batch)))
        q_value = torch.sum(current_prediction_batch * action_batch, dim=1)
        optimize.zero_grad()
        loss = criteria(q_value, y_batch)
        loss.backward()
        optimize.step()

        state = next_state
        i += 1

        if i % 1000 == 0:
            print("Iteration: {}/{}, Action: {}, Loss: {}, Epsilon {}, Reward: {}, Q-value: {}".format(
                i + 1,
                opt.num_iters,
                action,
                loss,
                epsilon, reward, torch.max(pred)))

        write.add_scalar('Train/Loss', loss, i)
        write.add_scalar('Train/Epsilon', epsilon, i)
        write.add_scalar('Train/Reward', reward, i)
        write.add_scalar('Train/Q-value', torch.max(pred), i)
        if (i+1) % 10000 == 0:
            print("ITERATION:", i)
        if (i+1) % 1000000 == 0:
            torch.save(model, "{}/flappy_bird_{}".format(opt.saved_path, i+1))
    
    torch.save(model, "{}/flappy_bird".format(opt.saved_path))

if __name__ == "__main__":
    train(find_args())