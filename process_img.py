import matplotlib.pyplot as plt
import matplotlib.image as mpimg

dst_img = mpimg.imread('dst.png')
pseudo_img = dst_img[:,:,0]

print(dst_img)
print()
print(pseudo_img)

plt.suptitle('Image Processing',fontsize=18)
plt.subplot(1,2,1)
plt.title('Original Image')
plt.imshow(mpimg.imread('red_flag.png'))

plt.subplot(1,2,2)
plt.title('Pseudocolor Image')
plt.imshow(pseudo_img)

plt.show()
