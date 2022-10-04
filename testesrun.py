import matplotlib.pyplot as plt

res_real = np.abs(np.real(Z_fit)-Re_Z)
res_im = np.abs(np.imag(Z_fit)-Im_Z)

sum_res_re = np.sum(res_real)
sum_res_im = np.sum(res_im)

frq_re = res_real/sum_res_re*100
frq_im = res_im/sum_res_im*100

plt.plot(freq, frq_re)
plt.plot(freq, frq_im)

import matplotlib.pyplot as plt
# Residual of Norm
res = abs(mod_z_fit - mod_z)
sum_res = np.sum(mod_z_fit - mod_z)
frq_res = res/sum_res*100
chi = (mod_z_fit - mod_z) ** 2 / mod_z_fit
sum_ = np.sum(chi)
frq_chi = chi/sum_*100
# Residual of real and imaginary part
res_real = np.abs(np.real(Z_fit)-Re_Z)
res_im = np.abs(abs(np.imag(Z_fit))-Im_Z)

frq_re = res_real/np.real(Z_fit)*100
frq_im = res_im/abs(np.imag(Z_fit))*100

fig, ax1 = plt.subplots()
ax1.set_xscale('log')
ax2 = ax1.twinx()
ax1.plot(freq, mod_z, 'b.')
ax1.plot(freqX, modZfitY, 'b-')
ax2.plot(freq, frq_chi, 'r')






