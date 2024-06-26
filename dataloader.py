import cv2
import os
import json
import torchvision
import random
import os
import numpy as np
import torch
import torch.nn.functional as F
import cv2
from torch.utils.data import Dataset
from torch.autograd import Variable
 
from models.transforms import * 
import torchvision.transforms as transforms


def convert_video(video_path, dest):
    
    if not os.path.exists(dest):
        os.makedirs(dest)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    success, frame = cap.read()
    frame_count = 0

    while success:
        frame_filename = os.path.join(dest, f"{frame_count}.jpg")
        cv2.imwrite(frame_filename, frame)
        success, frame = cap.read()
        frame_count += 1

    cap.release()

    print(f"Video converted to frames. {frame_count} frames saved in {dest}")



 
 
class VideoClassificationDataset(Dataset):
    def __init__(self, opt, mode):
        # python 3
        # super().__init__()
        super(VideoClassificationDataset, self).__init__()
        self.mode = mode  # to load train/val/test data
        self.feats_dir = opt['feats_dir']
        if self.mode == 'val':
            self.n = 200          #提取的视频数量
        if self.mode != 'inference':
            print(f'load feats from {self.feats_dir}')
 
            with open(self.feats_dir) as f:
                feat_class_list = f.readlines()
            self.feat_class_list = feat_class_list
    
            mean =[0.485, 0.456, 0.406]
            std = [0.229, 0.224, 0.225]
   
            model_transform_params  = {
                "side_size": 256,
                "crop_size": 224,
                "num_segments": 8,
                "sampling_rate": 5
            }
 
            # Get transform parameters based on model
            transform_params = model_transform_params
            
            transform_train = torchvision.transforms.Compose([
                       GroupMultiScaleCrop(transform_params["crop_size"], [1, .875, .75, .66]),
                       GroupRandomHorizontalFlip(is_flow=False),
                       Stack(roll=False),
                       ToTorchFormatTensor(div=True),
                       GroupNormalize(mean, std),
                   ])
            
            transform_val = torchvision.transforms.Compose([
                       GroupScale(int(transform_params["side_size"])),
                       GroupCenterCrop(transform_params["crop_size"]),
                       Stack(roll=False),
                       ToTorchFormatTensor(div=True),
                       GroupNormalize(mean, std),
                   ])
        
            self.transform_params = transform_params
            self.transform_train = transform_train
            self.transform_val = transform_val
 
        print("Finished initializing dataloader.")
 
    def __getitem__(self, ix):
        """This function returns a tuple that is further passed to collate_fn
        """
        ix = ix % self.n
        fc_feat = self._load_video(ix)
 
        data = {
            'fc_feats': Variable(fc_feat),
            'video_id': ix,
        }
 
        return data
 
    def __len__(self):
        return self.n
 
    def _load_video(self, idx):
        prefix = '{:05d}.jpg'
        feat_path_list = []
        for i in range(len(self.feat_class_list)):
            video_name = self.feat_class_list[i].rstrip('\n').split('\t')[0]+'-'
            feat_path = self.feat_class_list[i].rstrip('\n').split('\t')[1]
            feat_path_list.append(feat_path)
 
        video_data = {}

        # print(len(feat_path_list))
        # print(idx)
        if self.mode == 'val':
            images = []
            frame_list =os.listdir(feat_path_list[idx])
            average_duration = len(frame_list) // self.transform_params["num_segments"]
            # offests为采样坐标
            offsets = np.array([int(average_duration / 2.0 + average_duration * x) for x in range(self.transform_params["num_segments"])])
            offsets = offsets + 1
            for seg_ind in offsets:
                p = int(seg_ind)
                seg_imgs = Image.open(os.path.join(feat_path_list[idx], prefix.format(p))).convert('RGB')
                images.append(seg_imgs)
            video_data = self.transform_val(images)
            video_data = video_data.view((-1, self.transform_params["num_segments"]) + video_data.size()[1:])
 
        return video_data






# video_path = "/Users/liyun/Desktop/Anomaly-Videos-Part-1/Abuse/Abuse001_x264.mp4"
# dest = '/Users/liyun/Desktop/Anomaly-frames'
 
# convert_video(video_path, dest)
