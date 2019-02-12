# -*- coding:utf-8 -*-  
from __future__ import print_function
import scipy
import numpy as np
import os
import sys
import time
import random
import math
import cv2
from tqdm import tqdm 

def read_img(p):
    path, y = p[0], p[1]
    x = cv2.imread(path)
    x = cv2.cvtColor(x, cv2.COLOR_RGB2BGR)
    return x, y

    
def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    
class FileDirReader:
    def __init__(self, datadir, balance = False, name='--'):
        self.setname = name
        self.datadir = datadir
        self.celeb = []
        self.dict = {}
        self.list = []
        self.ibuf = []
        self.balance = balance
        self.cursor = 0
        self.cid = 0
        self.cbuf = []
        self.id_offset = 0
        # scan files
        subdirs = os.listdir(datadir)
        subdirs.sort()
        label = 0
        index = 0
        self.dict = {}
        bar = tqdm(total=len(subdirs))
        for subdir in subdirs:
            fullpath = os.path.join(datadir,subdir)
            bar.update(1)
            if not os.path.isdir(fullpath):
                continue
            filenames = os.listdir(fullpath)
            count = 0
            sub_list = []
            for filename in filenames:
                if not allowed_file(filename):
                    continue
                filepath = os.path.join(subdir, filename)
                self.list.append((filepath, label))
                sub_list.append(index)
                index += 1
            if sub_list:
                self.dict[label] = sub_list
                label += 1
        self.celeb = [x for x in range(label)]
        self.ibuf = [x for x in range(len(self.list))]
        self.shuffle()
        self.verbose()

    def setBalance(self, balance):
        self.balance = balance
        
    def name(self):
        return self.setname
        
    def add(self, line):
        pass

    def reset(self):
        self.cursor = 0
        self.cid = 0
        self.cbuf = [i for i in range(len(self.celeb))]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.ibuf)
        
        
    def digest(self):
        pass

    def verbose(self):
        print('Dataset:%8s size:%6d nclass:%d' % (self.setname, self.size(), self.numOfClass()))
        
    def size(self):
        return len(self.list)

    def numOfClass(self):
        return len(self.celeb)

    def maxClass(self):
        return max(self.celeb)
    
    def minClass(self):
        return min(self.celeb)
        
    def getSample(self,index):
        if self.balance:
            # balanced
            if self.cid >= len(self.celeb):
                random.shuffle(self.cbuf)
                self.cid = 0
            label = self.celeb[self.cbuf[self.cid]]
            index = np.random.choice(self.dict[label])
            self.cid += 1
        else:
            index = self.ibuf[index]
        item = self.list[index]
        rel_path = item[0]
        path = os.path.join(self.datadir, rel_path)
        return path, item[1]
        
    def next(self):
        '''
        Return audio path, and label 
        '''
        index = self.cursor
        if index >= self.size():
            raise StopIteration
        self.cursor += 1
        path, label = self.getSample(index)
        return read_img((path, label))
   
    
    def nextTask(self):
        path, y = self.next()
        return (read_img, (path, y))
        
    def moreTask(self, y):
        index = np.random.choice(self.dict[y])
        item = self.list[index]
        rel_path = item[0]
        path = os.path.join(self.datadir, rel_path)
        return (read_img, (path, y))
        
    def close(self):
        self.celeb = []
        self.dict = {}
        self.list = []
        print("%s closed"%(self.name()))
        
if __name__ == '__main__':
    reader = FileDirReader('E:/data/faces_glintasia_snap80')
    pass
    