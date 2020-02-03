import matplotlib.pyplot as plt
import skimage.io
import numpy as np
import scipy.misc

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

def _tf_fspecial_gauss(size, sigma=1.5):
    x_data, y_data = np.mgrid[-size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1]

    x_data = np.expand_dims(x_data, axis=-1)
    x_data = np.expand_dims(x_data, axis=-1)

    y_data = np.expand_dims(y_data, axis=-1)
    y_data = np.expand_dims(y_data, axis=-1)

    x = tf.constant(x_data, dtype=tf.float32)
    y = tf.constant(y_data, dtype=tf.float32)

    g = tf.exp(-((x**2 + y**2)/(2.0*sigma**2)))
    return g / tf.reduce_sum(g)


def SSIM(img1, img2, k1=0.01, k2=0.02, L=1, window_size=11):
    """
    The function is to calculate the ssim score
    """

    img1 = tf.expand_dims(img1, 0)
    img1 = tf.expand_dims(img1, -1)
    img2 = tf.expand_dims(img2, 0)
    img2 = tf.expand_dims(img2, -1)

    window = _tf_fspecial_gauss(window_size)

    mu1 = tf.nn.conv2d(img1, window, strides = [1, 1, 1, 1], padding = 'VALID')
    mu2 = tf.nn.conv2d(img2, window, strides = [1, 1, 1, 1], padding = 'VALID')

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = tf.nn.conv2d(img1*img1, window, strides = [1 ,1, 1, 1], padding = 'VALID') - mu1_sq
    sigma2_sq = tf.nn.conv2d(img2*img2, window, strides = [1, 1, 1, 1], padding = 'VALID') - mu2_sq
    sigma1_2 = tf.nn.conv2d(img1*img2, window, strides = [1, 1, 1, 1], padding = 'VALID') - mu1_mu2

    c1 = (k1*L)**2
    c2 = (k2*L)**2

    ssim_map = ((2*mu1_mu2 + c1)*(2*sigma1_2 + c2)) / ((mu1_sq + mu2_sq + c1)*(sigma1_sq + sigma2_sq + c2))

    return tf.reduce_mean(ssim_map)

def tf_log10(x):
    numerator = tf.log(x)
    denominator = tf.log(tf.constant(10, dtype=numerator.dtype))
    return numerator / denominator

def PSNR(y_true, y_pred):
    max_pixel = 255.0
    return 10.0 * tf_log10((max_pixel ** 2) / (tf.reduce_mean(tf.square(y_pred - y_true))))

if __name__ == '__main__':
    img1 = np.array(scipy.misc.imread('Figure_3.png', mode='RGB').astype('float32'))
    img2 = np.array(scipy.misc.imread('Figure_2.png', mode='RGB').astype('float32'))

    img1 = tf.constant(img1)
    img2 = tf.constant(img2)

    _SSIM_ = tf.image.ssim(img1, img2, 1.0)
    _PSNR_ = tf.image.psnr(img1, img2, 255.0)

    rgb1 = tf.unstack(img1, axis=2)
    r1 = rgb1[0]
    g1 = rgb1[1]
    b1 = rgb1[2]
    label = '{MSE :.2f,    SSIM :.2f}'
    rgb2 = tf.unstack(img2, axis=2)
    r2 = rgb2[0]
    g2 = rgb2[1]
    b2 = rgb2[2]

    ssim_r=SSIM(r1,r2)
    ssim_g=SSIM(g1,g2)
    ssim_b=SSIM(b1,b2)

    ssim = tf.reduce_mean(ssim_r+ssim_g+ssim_b)/3
    psnr = PSNR(img1, img2)


    with tf.Session() as sess:
        print(sess.run(_SSIM_))

        print(sess.run(ssim))
        image1 = skimage.io.imread('Figure_3.png')
        image2 = skimage.io.imread('Figure_4.png')
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4), sharex=True, sharey=True)
        ax = axes.ravel()
        ax[0].imshow(image1, cmap=plt.cm.gray, vmin=0, vmax=1)
        ax[0].set_xlabel(sess.run(_SSIM_))
        ax[0].set_title('origin')

        ax[1].imshow(image2, cmap=plt.cm.gray, vmin=0, vmax=1)
        ax[1].set_xlabel(sess.run(ssim))
        ax[1].set_title('visual')
        plt.tight_layout()
        plt.show()
