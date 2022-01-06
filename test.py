import argparse

import cv2
import numpy as np
import torch

from deep_q_learning import DeepQNetwork
from flappy_qlearning import Flappy

def process_image(image, w=84, h=84):
    image = cv2.resize(np.array(image), (w, h))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
    return image[None, :, :].astype(np.float32)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-size", type=int, default=84)
    parser.add_argument("--saved-path", type=str, default="models/flappy_bird_2000000")  
    return parser.parse_args()

def test(opt):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
        model = torch.load(opt.saved_path)
    else:
        torch.manual_seed(123)
        model = torch.load(opt.saved_path, map_location=lambda storage, loc: storage)
    model.eval()
    gamestate = Flappy()
    image, _, _ = gamestate.next_frame(0)
    #image = process_image(image[:500, :300], opt.image_size, opt.image_size)
    #image = process_image(image, opt.image_size, opt.image_size)
    image = process_image(image)
    image = torch.from_numpy(image)
    if torch.cuda.is_available():
        model.cuda()
        image = image.cuda()
    state = torch.cat(tuple(image for _ in range(4)))[None, :, :, :]

    while True:
        pred = model(state)[0]
        action = torch.argmax(pred)[0]
        next_image, _, _ = gamestate.next_frame(action)
        #next_image = process_image(image[:500, :300], opt.image_size, opt.image_size)
        next_image = process_image(image, opt.image_size, opt.image_size)
        #next_image = process_image(image)
        next_image = torch.from_numpy(next_image)
        if torch.cuda.is_available():
            next_image = next_image.cuda()
        state = torch.cat((state[0, 1:, :, :], next_image))[None, :, :, :]

if __name__ == "__main__":
    opt = get_args()
    test(opt)