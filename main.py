import argparse
import os
import torch
import numpy as np
from torch.utils.data import DataLoader
import random
from dataloader import VideoClassificationDataset
from timesformer.models.vit import TimeSformer
 
device = torch.device("cpu")
 
if __name__ == '__main__':
    opt = argparse.ArgumentParser()
    opt.add_argument('test_list_dir',  nargs='?', default='/Users/liyun/Desktop/video.txt', help="Directory where test features are stored.")
    
    opt = vars(opt.parse_args())
 
    test_opts = {'feats_dir': opt['test_list_dir']}
 
    # set up the model
    model = TimeSformer(img_size=224, num_classes=400, num_frames=8, attention_type='divided_space_time',
                        pretrained_model='/Users/liyun/Downloads/TimeSformer_divST_8x32_224_K600.pyth')
 
    model = model.eval().to(device)
    print(model)
 
    # load the data
    # print("Use", torch.cuda.device_count(), 'gpus')
    test_loader = {}
 
    test_dataset = VideoClassificationDataset(test_opts, 'val')
    test_loader = DataLoader(test_dataset, batch_size=1, num_workers=6, shuffle=False)
 
    # validation
    i = 0
    file1 = open("/Users/liyun/Desktop/video.txt", 'r')
    file1_list = file1.readlines()
    for data in test_loader:
        model_input = data['fc_feats'].to(device)
        name_feature = file1_list[i].rstrip().split('\t')[0].split('.')[0]
        i = i + 1
        out = model(model_input, )
        out = out.squeeze(0)
        out = out.cpu().detach().numpy()

        output_dir = '/Users/liyun/Desktop/output/'
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        np.save(os.path.join(output_dir, name_feature + '.npy'), out)
        # np.save('/Users/liyun/Desktop/output/' + name_feature + '.npy', out)
        print(i)
