# Use MC3 to find PWV

import sys
import numpy as np

sys.path.append("/Users/ashbake/Documents/ResearchKavli/Code/PB062816clouds/pyratbay/modules/MCcubed/")
import MCcubed as mc3

# Run loadCAMAL.py
#execfile('loadCAMAL.py')

# Load Data:
data   = np.array([np.median(y[0]),np.median(y[1])])
uncert = np.array([0.03,0.01])
def model(p0,tel_eff,yspec,yray,ytap,cv):
    PWV = p0[0]
    a   = p0[1]
    trans_t = tel_eff * yspec * yray**1.9 * np.abs(ytap)**(PWV/cv)
    f1 = a * 0.34 * 0.97 * tl.integrate(xtap,filters[0]*0.01* trans_t)
    f2 = 0.26 * tl.integrate(xtap,filters[1]*0.01* trans_t)
    f3 = 0.19 * tl.integrate(xtap,filters[2]*0.01* trans_t)
    return np.array([f2/f1, f3/f1])

# Fit the quad polynomial coefficients:
params   = np.array([10.0,1.0])  # Initial guess of fitting params.
stepsize = np.array([0.05,0.01])

# Run the MCMC:
f = mc3.mcmc(data, uncert,
    func=model, indparams=[tel_eff,yspec,yray,ytap,cv], params=params, stepsize=stepsize,
    nsamples=10e3, burnin=100)

posterior = f[2]

# Plot best-fitting model and binned data:
mc3.plots.modelfit(data, uncert, np.array([0,1]), data, title="Best-fitting Model",
                   savefile="quad_bestfit.png")
# Plot trace plot:
parname = ["PWV","a"]
mc3.plots.trace(posterior, Zchain, title="Fitting-parameter Trace Plots",
                parname=parname, savefile="quad_trace.png")

# Plot pairwise posteriors:
mc3.plots.pairwise(posterior, title="Pairwise posteriors", parname=parname,
                   savefile="quad_pairwise.png")

# Plot marginal posterior histograms:
mc3.plots.histogram(posterior, title="Marginal posterior histograms",
              parname=parname, savefile="quad_hist.png", percentile=0.683)

