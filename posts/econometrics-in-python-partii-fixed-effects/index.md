---
date: "2018-02-20"
layout: post
title: Econometrics in Python Part II - Fixed effects
categories: [code, econometrics, python]
---


In this second in a series on econometrics in Python, I'll look at how to implement fixed effects.

For inspiration, I'll use a recent NBER working paper by Azar, Marinescu, and Steinbaum on [Labor Market Concentration](http://www.nber.org/papers/w24147). In their paper, they look at the monopsony power of firms to hire staff in over 8,000 geographic-occupational labor markets in the US, finding that "going from the 25th percentile to the 75th percentile in concentration is associated with a 17% decline in posted wages". I'll use a vastly simplified version of their model. Their measure of concentration is denoted $\text{HHI}$, and they look at how this affects $\ln(w)$, the log of the real wage. The model has hiring observations which are organised by year-quarter, labelled $t$, and market (commuting zone-occupation), $m$:

$$
\ln(w_{m,t}) = \beta \cdot\text{HHI}+\alpha_t+\nu_m+\epsilon
$$

where $\alpha_t$ is a fixed year-quarter effect, and $\nu_m$ is a fixed market effect.

### The code

The most popular statistics module in Python is ```statsmodels```, but ```pandas``` and ```numpy``` make data manipulation and creation easy.

```python
import pandas as pd
import statsmodels.formula.api as sm
import numpy as np
```

As far as I can see the data behind the paper is not available, so the first job is to create some **synthetic data** for which the answer, the value of $\beta$, is known. I took the rough value for $\beta$ from the paper, but the other numbers are made up.

```python
np.random.seed(15022018)
# Synthetic data settings
commZonesNo = 15
yearQuarterNo = 15
numObsPerCommPerYQ = 1000
beta = -0.04
HHI =np.random.uniform(3.,6.,size=[commZonesNo,
                            yearQuarterNo,
                            numObsPerCommPerYQ])

# Different only in first index (market)
cZeffect =np.tile(np.tile(np.random.uniform(high=10.,
                                            size=commZonesNo),
                           (yearQuarterNo,1)),(numObsPerCommPerYQ,1,1)).T
cZnames = np.tile(np.tile(['cZ'+str(i) for i in range(commZonesNo)],
                           (yearQuarterNo,1)),(numObsPerCommPerYQ,1,1)).T
# Different only in second index (year-quarter)
yQeffect = np.tile(np.tile(np.random.uniform(high=10.,
                                             size=yearQuarterNo),
                           (numObsPerCommPerYQ,1)).T,(commZonesNo,1,1))
yQnames = np.tile(np.tile(['yQ'+str(i) for i in range(yearQuarterNo)],
                           (numObsPerCommPerYQ,1)).T,(commZonesNo,1,1))
# commZonesNo x yearQuarterNo x obs error matrix
HomoErrorMat = np.random.normal(size=[commZonesNo,
                                      yearQuarterNo,
                                      numObsPerCommPerYQ])

logrealwage = beta*HHI+cZeffect+yQeffect+HomoErrorMat
df = pd.DataFrame({'logrealwage':logrealwage.flatten(),
                  'HHI':HHI.flatten(),
                  'Cz':cZnames.flatten(),
                  'yQ':yQnames.flatten()})
print(df.head())
```

        Cz       HHI  logrealwage   yQ
    0  cZ0  5.175476     5.683932  yQ0
    1  cZ0  4.829876     4.732797  yQ0
    2  cZ0  5.284036     5.261500  yQ0
    3  cZ0  4.024909     4.027340  yQ0
    4  cZ0  3.674694     3.802822  yQ0


Running the regressions is very easy as statsmodels can use the [patsy package](https://patsy.readthedocs.io/en/v0.1.0/overview.html), which is based on similar equation parsers in R and S. Here's the normal OLS measure:

```python
normal_ols = sm.ols(formula='logrealwage ~ HHI',
                          data=df).fit()
print(normal_ols.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:            logrealwage   R-squared:                       0.000
    Model:                            OLS   Adj. R-squared:                  0.000
    Method:                 Least Squares   F-statistic:                     23.39
    Date:                Fri, 16 Feb 2018   Prob (F-statistic):           1.32e-06
    Time:                        23:20:13   Log-Likelihood:            -6.3063e+05
    No. Observations:              225000   AIC:                         1.261e+06
    Df Residuals:                  224998   BIC:                         1.261e+06
    Df Model:                           1                                         
    Covariance Type:            nonrobust                                         
    ==============================================================================
                     coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------
    Intercept      9.6828      0.044    217.653      0.000       9.596       9.770
    HHI           -0.0470      0.010     -4.837      0.000      -0.066      -0.028
    ==============================================================================
    Omnibus:                     5561.458   Durbin-Watson:                   0.127
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             4713.381
    Skew:                           0.289   Prob(JB):                         0.00
    Kurtosis:                       2.590   Cond. No.                         25.3
    ==============================================================================

    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

As an aside, the intercept can be suppressed by using 'logrealwage ~ HHI-1' rather than 'logrealwage ~ HHI'. The straight OLS approach does not do a terrible job for the point estimate, but the $R^2$ is terrible. Fixed effects can get us out of the, er, fix...

```python
FE_ols = sm.ols(formula='logrealwage ~ HHI+C(Cz)+C(yQ)-1',
                              data=df).fit()
print(FE_ols.summary())
```

                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:            logrealwage   R-squared:                       0.937
    Model:                            OLS   Adj. R-squared:                  0.937
    Method:                 Least Squares   F-statistic:                 1.154e+05
    Date:                Fri, 16 Feb 2018   Prob (F-statistic):               0.00
    Time:                        23:20:31   Log-Likelihood:            -3.1958e+05
    No. Observations:              225000   AIC:                         6.392e+05
    Df Residuals:                  224970   BIC:                         6.395e+05
    Df Model:                          29                                         
    Covariance Type:            nonrobust                                         
    =================================================================================
                        coef    std err          t      P>|t|      [0.025      0.975]
    ---------------------------------------------------------------------------------
    C(Cz)[cZ0]        4.4477      0.016    281.428      0.000       4.417       4.479
    C(Cz)[cZ1]       10.0441      0.016    636.101      0.000      10.013      10.075
    C(Cz)[cZ10]      10.4897      0.016    663.407      0.000      10.459      10.521
    C(Cz)[cZ11]      12.2364      0.016    773.920      0.000      12.205      12.267
    C(Cz)[cZ12]       8.7909      0.016    556.803      0.000       8.760       8.822
    C(Cz)[cZ13]       8.6307      0.016    545.917      0.000       8.600       8.662
    C(Cz)[cZ14]      12.1590      0.016    768.937      0.000      12.128      12.190
    C(Cz)[cZ2]       11.5722      0.016    733.999      0.000      11.541      11.603
    C(Cz)[cZ3]        7.4164      0.016    469.160      0.000       7.385       7.447
    C(Cz)[cZ4]       10.4830      0.016    663.719      0.000      10.452      10.514
    C(Cz)[cZ5]        6.2675      0.016    396.634      0.000       6.237       6.299
    C(Cz)[cZ6]        7.1924      0.016    455.045      0.000       7.161       7.223
    C(Cz)[cZ7]        5.2567      0.016    333.177      0.000       5.226       5.288
    C(Cz)[cZ8]        6.3380      0.016    401.223      0.000       6.307       6.369
    C(Cz)[cZ9]        5.8814      0.016    372.246      0.000       5.850       5.912
    C(yQ)[T.yQ1]      0.1484      0.012     12.828      0.000       0.126       0.171
    C(yQ)[T.yQ10]    -2.2139      0.012   -191.442      0.000      -2.237      -2.191
    C(yQ)[T.yQ11]    -0.2461      0.012    -21.280      0.000      -0.269      -0.223
    C(yQ)[T.yQ12]     3.0241      0.012    261.504      0.000       3.001       3.047
    C(yQ)[T.yQ13]    -2.0663      0.012   -178.679      0.000      -2.089      -2.044
    C(yQ)[T.yQ14]     2.9468      0.012    254.817      0.000       2.924       2.969
    C(yQ)[T.yQ2]      2.0992      0.012    181.520      0.000       2.076       2.122
    C(yQ)[T.yQ3]      5.0328      0.012    435.196      0.000       5.010       5.055
    C(yQ)[T.yQ4]      7.4619      0.012    645.253      0.000       7.439       7.485
    C(yQ)[T.yQ5]     -0.9819      0.012    -84.907      0.000      -1.005      -0.959
    C(yQ)[T.yQ6]     -2.0630      0.012   -178.396      0.000      -2.086      -2.040
    C(yQ)[T.yQ7]      5.4874      0.012    474.502      0.000       5.465       5.510
    C(yQ)[T.yQ8]     -1.5476      0.012   -133.824      0.000      -1.570      -1.525
    C(yQ)[T.yQ9]      0.2312      0.012     19.989      0.000       0.208       0.254
    HHI              -0.0363      0.002    -14.874      0.000      -0.041      -0.031
    ==============================================================================
    Omnibus:                        0.866   Durbin-Watson:                   1.994
    Prob(Omnibus):                  0.648   Jarque-Bera (JB):                0.873
    Skew:                           0.003   Prob(JB):                        0.646
    Kurtosis:                       2.993   Cond. No.                         124.
    ==============================================================================

    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


This is much closer to the right answer of $\beta=-0.04$, has half the standard error, and explains much more of the variation in $\ln(w_{m,t})$.
