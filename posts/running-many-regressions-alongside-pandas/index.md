---
date: "2018-05-05"
layout: post
title: Econometrics in Python Part IV - Running many regressions alongside pandas
categories: [code, econometrics, python]
---
*The fourth in the series of posts covering econometrics in Python. This time: automating the boring business of running multiple regressions on columns in a pandas dataframe.*

Data science in Python *is* the open source package [pandas](https://pandas.pydata.org/), more or less. It's an amazing, powerful library and the firms, researchers, and governments who use it are indebted to its maintainers, including [Wes McKinney](http://wesmckinney.com/).

When data arrive in your Python code, they're most likely going to arrive in a pandas dataframe. If you're doing econometrics, you're then likely to want to do regressions from the dataframe with the minimum of fuss and the maximum of flexibility. This post sets out a way to do that with a few extra functions.

There are two main ways to run regressions in Python: [statsmodels](https://www.statsmodels.org/stable/index.html) or [scikit-learn](http://scikit-learn.org/stable/). The latter is more geared toward machine learning, so I'll be using the former for regressions. The typical way to do this might be the following (ignoring imports and data importing), with a pandas dataframe ```df``` with an x-variable 'concrete' and a y-variable 'age':

```python
mod = sm.OLS(df['Age'],df['Concrete'])
results = mod.fit()
print(results.summary())
```


                                OLS Regression Results                            
    ==============================================================================
    Dep. Variable:                    Age   R-squared:                       0.414
    Model:                            OLS   Adj. R-squared:                  0.414
    Method:                 Least Squares   F-statistic:                     728.1
    Date:                     05 May 2018   Prob (F-statistic):          1.05e-121
    Time:                        00:00:00   Log-Likelihood:                -5672.3
    No. Observations:                1030   AIC:                         1.135e+04
    Df Residuals:                    1029   BIC:                         1.135e+04
    Df Model:                           1                                         
    Covariance Type:            nonrobust                                         
    ==============================================================================
                     coef    std err          t      P>|t|      [0.025      0.975]
    ------------------------------------------------------------------------------
    Concrete       1.2693      0.047     26.984      0.000       1.177       1.362
    ==============================================================================
    Omnibus:                      761.497   Durbin-Watson:                   0.998
    Prob(Omnibus):                  0.000   Jarque-Bera (JB):             9916.238
    Skew:                           3.411   Prob(JB):                         0.00
    Kurtosis:                      16.584   Cond. No.                         1.00
    ==============================================================================

    Warnings:
    [1] Standard Errors assume that the covariance matrix of the errors is correctly specified.


In the rest of this post I will outline a more flexible and extensible way of doing this, which will allow for multiple models and controls, with code snippets you can copy, paste, and then forget about.

## Loading the data
Our data are on the compressive strength of concrete - I know, brilliant, and we could talk more about the [fascinating history of concrete](https://www.npr.org/2012/02/17/147047553/concretes-role-as-a-building-block-in-history) and its [importance for the economy](https://www.bbc.co.uk/programmes/p04gyg20), but we should get to the stats. The data are from the UC Irvine Machine Learning datasets repository; [see here for them](http://archive.ics.uci.edu/ml/datasets/Concrete+Compressive+Strength).

```python
df = pd.read_excel('concrete_data.xls')
df.head()
```


       Cement (component 1)(kg in a m^3 mixture)  \
    0                                      540.0   
    1                                      540.0   
    2                                      332.5   
    3                                      332.5   
    4                                      198.6   

       Blast Furnace Slag (component 2)(kg in a m^3 mixture)  \
    0                                                0.0       
    1                                                0.0       
    2                                              142.5       
    3                                              142.5       
    4                                              132.4       

       Fly Ash (component 3)(kg in a m^3 mixture)  \
    0                                         0.0   
    1                                         0.0   
    2                                         0.0   
    3                                         0.0   
    4                                         0.0   

       Water  (component 4)(kg in a m^3 mixture)  \
    0                                      162.0   
    1                                      162.0   
    2                                      228.0   
    3                                      228.0   
    4                                      192.0   

       Superplasticizer (component 5)(kg in a m^3 mixture)  \
    0                                                2.5     
    1                                                2.5     
    2                                                0.0     
    3                                                0.0     
    4                                                0.0     

       Coarse Aggregate  (component 6)(kg in a m^3 mixture)  \
    0                                             1040.0      
    1                                             1055.0      
    2                                              932.0      
    3                                              932.0      
    4                                              978.4      

       Fine Aggregate (component 7)(kg in a m^3 mixture)  Age (day)  \
    0                                              676.0         28   
    1                                              676.0         28   
    2                                              594.0        270   
    3                                              594.0        365   
    4                                              825.5        360   

       Concrete compressive strength(MPa, megapascals)   
    0                                         79.986111  
    1                                         61.887366  
    2                                         40.269535  
    3                                         41.052780  
    4                                         44.296075  


Those column names are rather long! I'll just take the first word of each column name, and take a quick look at the data:

```python
df = df.rename(columns=dict(zip(df.columns,[x.split()[0] for x in df.columns])))
df.describe()
```



                Cement        Blast          Fly        Water  Superplasticizer  \
    count  1030.000000  1030.000000  1030.000000  1030.000000       1030.000000   
    mean    281.165631    73.895485    54.187136   181.566359          6.203112   
    std     104.507142    86.279104    63.996469    21.355567          5.973492   
    min     102.000000     0.000000     0.000000   121.750000          0.000000   
    25%     192.375000     0.000000     0.000000   164.900000          0.000000   
    50%     272.900000    22.000000     0.000000   185.000000          6.350000   
    75%     350.000000   142.950000   118.270000   192.000000         10.160000   
    max     540.000000   359.400000   200.100000   247.000000         32.200000   

                Coarse         Fine          Age     Concrete  
    count  1030.000000  1030.000000  1030.000000  1030.000000  
    mean    972.918592   773.578883    45.662136    35.817836  
    std      77.753818    80.175427    63.169912    16.705679  
    min     801.000000   594.000000     1.000000     2.331808  
    25%     932.000000   730.950000     7.000000    23.707115  
    50%     968.000000   779.510000    28.000000    34.442774  
    75%    1029.400000   824.000000    56.000000    46.136287  
    max    1145.000000   992.600000   365.000000    82.599225  

## Defining functions to run regressions
Let's set up a function which we can pass a dataframe to in order to run regressions on selected columns:
```python
def RegressionOneModel(df,Xindvars,Yvar,summary=True):

    if(type(Yvar)==str):
        Yvar=[Yvar]
    if(len(Yvar)!=1):
        print("Error: please enter a single y variable")
        return np.nan
    else:
        xf = df.dropna(subset=Yvar+Xindvars)[Xindvars+Yvar]
        Xexog = xf[Xindvars]
        model = sm.OLS(xf[Yvar].dropna(),Xexog)
        reg = model.fit()
    if(summary):
        return reg.summary2()
    else:
        return reg
```
How this does work? It's easiest to show with an example.
```python
regResults = RegressionOneModel(df,['Cement','Blast'],'Concrete')
print(regResults)
```


                     Results: Ordinary least squares
    ==================================================================
    Model:              OLS              Adj. R-squared:     0.878    
    Dependent Variable: Concrete         AIC:                8332.8955
    Date:               2018-05-05 00:00 BIC:                8342.7701
    No. Observations:   1030             Log-Likelihood:     -4164.4  
    Df Model:           2                F-statistic:        3705.    
    Df Residuals:       1028             Prob (F-statistic): 0.00     
    R-squared:          0.878            Scale:              190.64   
    ---------------------------------------------------------------------
              Coef.     Std.Err.       t       P>|t|     [0.025    0.975]
    ---------------------------------------------------------------------
    Cement    0.1079      0.0017    63.4736    0.0000    0.1046    0.1113
    Blast     0.0671      0.0045    14.9486    0.0000    0.0583    0.0760
    ------------------------------------------------------------------
    Omnibus:               7.719        Durbin-Watson:           0.983
    Prob(Omnibus):         0.021        Jarque-Bera (JB):        6.461
    Skew:                  0.117        Prob(JB):                0.040
    Kurtosis:              2.690        Condition No.:           3    
    ==================================================================




This function takes a variable number of X vectors and regresses Y ('concrete') on them. But what if we want to run many regressions at once? Fortunately ```statsmodels``` has some capability to do this. Unfortunately, it's not all that intuitive and, to use it with ease, we'll need to extend. I want it to be flexible enough so that it:
- works with X as a string, list, or a list of lists (for multiple models)
- accepts a number of controls which are the same in every model
- returns either a multi-model regression results summary or a single model summary as appropriate

To make this all work, we need a couple of extra functions. One just labels different models with Roman numerals and could be jettisoned. The other one is just a quick way of combining the variables to send to the regression.

```python
def write_roman(num):

    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])

def combineVarsList(X,Z,combine):
    if(combine):
        return X+Z
    else:
        return X
```

Finally, there is a function which decides how to call the underlying regression code, and which stitches the results from different models together:

```python
def RunRegression(df,XX,y,Z=['']):

    # If XX is not a list of lists, make it one -
    # - first by checking if type is string
    if(type(XX)==str):  # Check if it is one string
        XX = [XX]
     # - second for if it is a list
    if(not(any(isinstance(el, list) for el in XX))):
        XX = [XX]
    if(type(y)!=str): # Check y for string
        print('Error: please enter string for dependent variable')
        return np.nan
    title_string = 'OLS Regressions; dependent variable '+y
    # If Z is not a list, make it one
    if(type(Z)==str):
        Z = [Z]
    #XX = np.array(XX)
    # Check whether there is just a single model to run
    if(len(XX)==1):
        Xpassvars = list(XX[0])
        if(len(Z[0])!=0):
             Xpassvars = list(XX[0])+Z
        regRes = RegressionOneModel(df,Xpassvars,[y],summary=False)
        regResSum2 = regRes.summary2()
        regResSum2.add_title(title_string)
        return regResSum2
    elif(len(XX)>1):
        # Load in Z here if appropriate
        addControls = False
        if(len(Z[0])!=0):
             addControls = True
        # Case with multiple models
        info_dict={'R-squared' : lambda x: "{:.2f}".format(x.rsquared),
               'Adj. R-squared' : lambda x: "{:.2f}".format(x.rsquared_adj),
               'No. observations' : lambda x: "{0:d}".format(int(x.nobs))}
        regsVec = [RegressionOneModel(df,combineVarsList(X,Z,addControls),
                                              [y],summary=False) for X in XX]
        model_names_strList = ['Model '+\
                           write_roman(i) for i in range(1,len(XX)+1)]
        float_format_str = '%0.2f'
        uniqueVars = np.unique([item for sublist in XX for item in sublist])
        uniqueVars = [str(x) for x in uniqueVars]
        results_table = summary_col(results=regsVec,
                                float_format=float_format_str,
                                stars = True,
                                model_names=model_names_strList,
                                info_dict=info_dict,
                                regressor_order=uniqueVars+Z)
        results_table.add_title(title_string)
        return results_table
```
## Putting it all together

Let's see how it works. Firstly, the simple case of one y on one x.

```python
regResults = RunRegression(df,'Blast','Concrete')
print(regResults)
```


               OLS Regressions; dependent variable Concrete
    ==================================================================
    Model:              OLS              Adj. R-squared:     0.400    
    Dependent Variable: Concrete         AIC:                9971.8287
    Date:               2018-05-05 00:00 BIC:                9976.7660
    No. Observations:   1030             Log-Likelihood:     -4984.9  
    Df Model:           1                F-statistic:        688.0    
    Df Residuals:       1029             Prob (F-statistic): 1.57e-116
    R-squared:          0.401            Scale:              936.87   
    ---------------------------------------------------------------------
              Coef.     Std.Err.       t       P>|t|     [0.025    0.975]
    ---------------------------------------------------------------------
    Blast     0.2203      0.0084    26.2293    0.0000    0.2038    0.2367
    ------------------------------------------------------------------
    Omnibus:               39.762       Durbin-Watson:          0.477
    Prob(Omnibus):         0.000        Jarque-Bera (JB):       43.578
    Skew:                  -0.502       Prob(JB):               0.000
    Kurtosis:              3.081        Condition No.:          1     
    ==================================================================

Or several x variables:

```python
regResults = RunRegression(df,['Cement','Blast'],'Concrete')
print(regResults)
```


               OLS Regressions; dependent variable Concrete
    ==================================================================
    Model:              OLS              Adj. R-squared:     0.878    
    Dependent Variable: Concrete         AIC:                8332.8955
    Date:               2018-05-05 00:00 BIC:                8342.7701
    No. Observations:   1030             Log-Likelihood:     -4164.4  
    Df Model:           2                F-statistic:        3705.    
    Df Residuals:       1028             Prob (F-statistic): 0.00     
    R-squared:          0.878            Scale:              190.64   
    ---------------------------------------------------------------------
              Coef.     Std.Err.       t       P>|t|     [0.025    0.975]
    ---------------------------------------------------------------------
    Cement    0.1079      0.0017    63.4736    0.0000    0.1046    0.1113
    Blast     0.0671      0.0045    14.9486    0.0000    0.0583    0.0760
    ------------------------------------------------------------------
    Omnibus:               7.719        Durbin-Watson:           0.983
    Prob(Omnibus):         0.021        Jarque-Bera (JB):        6.461
    Skew:                  0.117        Prob(JB):                0.040
    Kurtosis:              2.690        Condition No.:           3    
    ==================================================================


Here comes the fun - to run multiple models, we need only pass a list of lists as the X variable in the function:

```python
Model_1_X = ['Cement', 'Blast']
Model_2_X = ['Coarse','Fine']
Model_3_X = ['Fly', 'Water']
ManyModelResults = RunRegression(df,
                                 [Model_1_X,Model_2_X,Model_3_X],
                                 'Concrete')
print(ManyModelResults)
```

    OLS Regressions; dependent variable Concrete
    ===========================================
                     Model I Model II Model III
    -------------------------------------------
    Blast            0.07***                   
                     (0.00)                    
    Cement           0.11***                   
                     (0.00)                    
    Coarse                   0.03***           
                             (0.00)            
    Fine                     0.01***           
                             (0.00)            
    Fly                               0.00     
                                      (0.01)   
    Water                             0.19***  
                                      (0.00)   
    R-squared        0.88    0.81     0.78     
    Adj. R-squared   0.88    0.81     0.78     
    No. observations 1030    1030     1030     
    ===========================================
    Standard errors in parentheses.
    * p<.1, ** p<.05, ***p<.01


There's a keyword argument, ```Z```, which we can pass controls (here just 'Age') via:

```python
ManyModelsWControl = RunRegression(df,
                                 [Model_1_X,Model_2_X,Model_3_X],
                                 'Concrete',
                                 Z = 'Age')
print(ManyModelsWControl)
```

    OLS Regressions; dependent variable Concrete
    ===========================================
                     Model I Model II Model III
    -------------------------------------------
    Blast            0.05***                   
                     (0.00)                    
    Cement           0.08***                   
                     (0.00)                    
    Coarse                   0.03***           
                             (0.00)            
    Fine                     -0.01**           
                             (0.00)            
    Fly                               -0.06***
                                      (0.01)   
    Water                             0.12***  
                                      (0.00)   
    Age              0.10*** 0.11***  0.10***  
                     (0.01)  (0.01)   (0.01)   
    Superplasticizer 1.04*** 1.44***  1.84***  
                     (0.06)  (0.08)   (0.08)   
    R-squared        0.92    0.87     0.88     
    Adj. R-squared   0.92    0.87     0.87     
    No. observations 1030    1030     1030     
    ===========================================
    Standard errors in parentheses.
    * p<.1, ** p<.05, ***p<.01

Finally, it's easy to pass multiple controls:

```python
ManyModelsWControls = RunRegression(df,
                                 [Model_1_X,Model_2_X,Model_3_X],
                                 'Concrete',
                                 Z = ['Age','Superplasticizer'])
print(ManyModelsWControls)
```

    OLS Regressions; dependent variable Concrete
    ===========================================
                     Model I Model II Model III
    -------------------------------------------
    Blast            0.05***                   
                     (0.00)                    
    Cement           0.08***                   
                     (0.00)                    
    Coarse                   0.03***           
                             (0.00)            
    Fine                     -0.01**           
                             (0.00)            
    Fly                               -0.06***
                                      (0.01)   
    Water                             0.12***  
                                      (0.00)   
    Age              0.10*** 0.11***  0.10***  
                     (0.01)  (0.01)   (0.01)   
    Superplasticizer 1.04*** 1.44***  1.84***  
                     (0.06)  (0.08)   (0.08)   
    R-squared        0.92    0.87     0.88     
    Adj. R-squared   0.92    0.87     0.87     
    No. observations 1030    1030     1030     
    ===========================================
    Standard errors in parentheses.
    * p<.1, ** p<.05, ***p<.01


By the way, the statsmodels summary object which is returned here has an .as_latex() method - useful if you want to dump results straight into papers.

Do you have a better way to quickly run many different kinds of OLS regressions from a pandas dataframe? Get in touch!

*NB: I had to remove the doc strings in the above code because they slowed down the page a lot.*
