import os
import torch
from torchsummary import summary
import argparse

from utils.tool import *
from utils.datasets import *
from utils.evaluation import CocoDetectionEvaluator

from module.detector import Detector

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if __name__ == '__main__':
    # 指定训练配置文件
    parser = argparse.ArgumentParser()
    parser.add_argument('--yaml', type=str, default="", help='.yaml config')
    parser.add_argument('--weight', type=str, default=None, help='.weight config')

    opt = parser.parse_args()
    assert os.path.exists(opt.yaml), "请指定正确的配置文件路径"
    assert os.path.exists(opt.weight), "请指定正确的权重文件路径"

    # 解析yaml配置文件
    cfg = LoadYaml(opt.yaml)    
    print(cfg) 

    # 加载模型权重
    print("load weight from:%s"%opt.weight)
    model = Detector(cfg.category_num, True).to(device)
    model.load_state_dict(torch.load(opt.weight))
    model.eval()

    # # 打印网络各层的张量维度
    summary(model, input_size=(3, cfg.input_height, cfg.input_width))