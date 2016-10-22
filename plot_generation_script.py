import numpy as np
import matplotlib.pyplot as plt
import sys
import pylab
#
# loads float array images (424x512xtot_ims) from binary file
#
def load_images_bin( filename ):

    infile = open(filename, "r")
    data = np.fromfile(infile, dtype=np.float32)

    tot_ims = len(data)/(512*424)
    #depth_images = np.empty((512, 424, tot_ims)) 
    depth_images = data.reshape(tot_ims,424, 512).transpose()
    return depth_images, tot_ims

#
# sets image points to inlier or outlier
#
def classify_depth_points(depth_images, ground_truth, inlier_threshold):

    sh = depth_images.shape

    mask_inliers = np.zeros(sh,dtype=bool) 
    mask_outliers = np.zeros(sh,dtype=bool) 
    print("sh[2] = ", sh[2])
    for i in range(0,sh[2]):
        mask_inliers[:,:,i] = (np.abs(ground_truth[:,:,0] - depth_images[:,:,i]) < inlier_threshold) & (ground_truth[:,:,0] > 0.0)
        #mask_inliers[np.where(inds),i] = 1
        mask_outliers[:,:,i] = (mask_inliers[:,:,i] != 1) & (ground_truth[:,:,0] > 0.0)
        #plt.figure(4)
        #plt.imshow(mask_outliers[:,:,i])
        #plt.figure(5)
        #plt.imshow(depth_images[:,:,i])
        #plt.show()
        #mask_outliers[np.where(inds),i] = 1

    return mask_inliers, mask_outliers

#
# calculates inlier/outlier rates
#
def generate_inlier_outlier_rates( max_vals_images, depth, ground_truth, inlier_threshold, num_points, num_images):

    sh = max_vals_images.shape
    print(sh)
    max_val_im = max_vals_images[:,:,1]
    sorted_max_vals = np.sort(max_val_im.ravel())
    len_max_val = len(sorted_max_vals)
    max_val_thresh = np.append(np.array(-0.0001), sorted_max_vals[::np.floor(len_max_val/num_points)])
    print(max_val_thresh, np.floor(len_max_val/num_points), len_max_val)
   
    num_thresh = len(max_val_thresh)
    print("num_thresh = ", num_thresh)
    mask_inliers, mask_outliers = classify_depth_points(depth, ground_truth, inlier_threshold)

    num_pixels = np.count_nonzero(ground_truth)
    num_inliers = np.zeros((num_images,num_thresh))
    num_outliers = np.zeros((num_images,num_thresh))

    for t in range(0,num_thresh):
        for i in range(0,num_images):
            mask = max_vals_images[:,:,i] > max_val_thresh[t]
            inliers = mask & mask_inliers[:,:,i]
            num_inliers[i,t] = np.count_nonzero(inliers.ravel())
            #print("num_inliers = ",num_inliers[i,t])
            outliers = mask & mask_outliers[:,:,i]
            num_outliers[i,t] = np.count_nonzero(outliers.ravel())
            
        #print("t = ",t)

    print("asdf", num_pixels)
    #print(num_inliers.shape)
    #print(num_inliers/num_pixels)
    inlier_rate = np.mean(num_inliers/num_pixels,axis=0)
    outlier_rate = np.mean(num_outliers/num_pixels,axis=0)
    inlier_rate_std = np.std(num_inliers/num_pixels,axis=0)
    outlier_rate_std = np.std(num_outliers/num_pixels,axis=0)
    thresholds = max_val_thresh

    return inlier_rate, outlier_rate, inlier_rate_std, outlier_rate_std, thresholds

def run_test(ground_truth_file, max_val_file, depth_images_file, inlier_threshold, num_points, fig_num):
    ground_truth, num_images = load_images_bin( ground_truth_file )
    max_val_images, num_images = load_images_bin( max_val_file )
    depth_images, num_images = load_images_bin( depth_images_file )
    print('max_val_images ', max_val_images.shape)
    print('depth_images', depth_images[300,300,1])
    print('ground_truth', ground_truth.shape)
    
    inlier_rate, outlier_rate, inlier_rate_std, outlier_rate_std, thresholds = generate_inlier_outlier_rates(max_val_images, depth_images, ground_truth, inlier_threshold, num_points, num_images)

    print(inlier_rate)
    plt.figure(fig_num)
    plt.clf()
    plt.plot(np.log(outlier_rate),inlier_rate,'-')
    plt.show()


def visualize_frame(args):
    depth_images_file = args[1]
    conf_images_file = args[2]
    frame = args[3]
    print('filename = ', depth_images_file, ' frame = ', frame)
    depth_images, num_images = load_images_bin( depth_images_file )
    conf_images, num_images = load_images_bin( conf_images_file )
    depth = depth_images[:,:,int(frame)].transpose()
    conf = conf_images[:,:,int(frame)].transpose()
    plt.figure(1)
    plt.imshow(depth,cmap=pylab.gray())
    plt.title('Depth image without outlier rejection')
    plt.figure(2)
    plt.imshow(conf,cmap=pylab.gray())
    plt.title('Confidence image')
    depth_filtered = np.array(depth)
    depth_filtered[np.where(conf < 0.4)] = 0.0
    plt.figure(3)
    plt.imshow(depth_filtered,cmap=pylab.gray())
    plt.title('Depth image with outlier rejection')
    plt.show()

# args: ['vis', 'depth_filename', 'conf_filename', frame_num] or ['test', 'path', 'ground_truth', {'microsoft_filename'}]
if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == 'vis':
        if len(args) < 4:
            print('not enough arguments')
            print('len(args) = ', len(args))
            exit()

        visualize_frame(args)
    elif args[0] == 'test':
        print('not implemented')
    else:
        print('not implemented')
