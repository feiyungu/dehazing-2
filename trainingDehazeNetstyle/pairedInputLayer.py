import caffe
from random import shuffle
import cv2

#prototxt:
#layer {
#    name: "data"
#    type: "Python"
#    top: "data"
#    top: "label"
#    python_param {
#        module: "pairedInputLayer"
#        layer: "pairedInput"
#        param_str :'{"data_folder": "/path", "label_folder": "/path",'\ 
#                   '"src_file": "/path/train.txt", "batch_size": 8,'\ 
#                   '"width": 550, "height": 413}'
#    }
#}

class pairedInput(caffe.Layer):
    def setup(self, bottom, top):
        if len(top) != 2:
            raise Exception("Need data and label defined")
        if len(bottom) != 0:
            raise Exception("Do not define a bottom")

        # Read parameters
        params = eval(self.param_str)
        self.data_folder = params["data_folder"]
        self.label_folder = params["label_folder"]
        src_file = params["src_file"]
        self.batch_size = params["batch_size"]
        self.width = params["width"]
        self.height = params["height"]

        # Reshape top
        # funny business is occurring here
        #top[0].reshape(self.batch_size, 3, self.height, self.width)
        #top[1].reshape(self.batch_size, 3, self.height, self.width)
        top[0].reshape(self.batch_size, 3, 460, 620)
        top[1].reshape(self.batch_size, 1, 215, 295)

        # Populate file list
        self.flist = [line.rstrip('\n') for 
                line in open(src_file)]
        shuffle(self.flist)
        self._cur = 0 # to check if need to restart list of images

###############################################################################
    def forward(self, bottom, top):
        for it in range(self.batch_size):
            im, label = self.load_next_image()
            # resize
            # funny business is occurring here
            #im = cv2.resize(im, (self.width, self.height))
            #label = cv2.resize(label, (self.width, self.height))
            im = cv2.resize(im, (620, 460))
            label = cv2.resize(label, (295, 215))
            # [0,255] -> [0,1]
            #im = im/255.0
            label = label/255.0
            # (H,W,C) -> (C,H,W)
            im = im.transpose((2,0,1))
            #label = label.transpose((2,0,1))
            # Add directly to top blob
            top[0].data[it, ...] = im
            top[1].data[it, ...] = label

###############################################################################
    def load_next_image(self):
        # If finished with all images, epoch is finished - time to start over
        if self._cur == len(self.flist):
            self._cur = 0
            shuffle(self.flist)
        
        # flist has lines of format 0001_0.8_0.04
        # training images are 0001_0.8_0.04.jpg
        # label images are 0001.jpg
        scene = self.flist[self._cur]
        base = scene.split("_")
        # 0 flag indicates grayscale
        label = cv2.imread(self.label_folder + "/" + base[0]+"_"+base[1] + ".png", 0)
        #label = cv2.imread(self.label_folder + "/" + base[0]+"_"+base[1] + ".png",1)
        im = cv2.imread(self.data_folder + "/" + scene + ".png")
        self._cur += 1
        return im, label

###############################################################################
    def reshape(self, bottom, top):
        # shouldn't need to reshape anything, right?
        pass

###############################################################################
    def backward(self, top, propagate_down, bottom):
        pass
