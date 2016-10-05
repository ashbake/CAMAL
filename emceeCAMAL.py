# -------------- -----------
# p: parameters
# p: tau1 tau2 m b1 b2 e780 e823 e860 


def lnprior(theta):
    # The parameters are stored as a vector of values, so unpack them
    tau, mstar, a = theta
    # We're using only uniform priors, and only eps has a lower bound
    if 0.3 < tau < 5.0 and 0.0 < mstar < 0.06 and 0.1 < a < 0.2:
        return 0
    return -np.inf



def lnlike(theta, x, y, yerr):
    """                                                                         
    Define Log Likelihood
    Eventually Based on two data sets
    """
    tau, mstar, a = theta
    model = getfakes(tau,mstar,a,x,filters)
    lp = 0
    # Loop through each filter ratio, sum all data points
    # Later can optimize tau for each 5 min bin
    for i, f in enumerate(model):
        inv_sigma2 = 1.0#/(yerr[i]**2)
        lp += -0.5*(np.sum((y[i]-f)**2*inv_sigma2 - np.log(inv_sigma2)))
    return lp


def lnprob(theta, x, y, yerr):
    lp = lnprior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike(theta, x, y, yerr)



import scipy.optimize as op
nll = lambda *args: -lnlike(*args)
result = op.minimize(nll, [3.0, 0.045, 0.13], args=(x, y, yerr))
print result["x"]


start_theta = (3.0, 0.045, 0.13)
ndim, nwalkers = 3, 50
pos = [start_theta + 1e-2*np.random.randn(ndim) for i in range(nwalkers)]

import emcee
sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(x, y, yerr))

sampler.run_mcmc(pos, 500)
samples = sampler.chain[:, 50:, :].reshape((-1, ndim))


import corner
fig = corner.corner(samples, labels=["$ tau $", "$m_*$", "$a$"])
          # , truths=[m_true, b_true])
fig.savefig("triangle_nwalk_50_its_500.png")


plt.figure(10)
fig, ax = plt.subplots(3)
samples = sampler.chain.reshape((-1, ndim))
ax[0].plot(samples[:,0])
ax[1].plot(samples[:,1])
ax[2].plot(samples[:,2])
