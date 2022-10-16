---
date: "2018-07-11"
layout: post
title: Why the latest, most exciting thing in machine learning is... game theory
categories: [research, machine-learning]
---


*And when I say latest, this particular method was invented in 1953.*

Machine learning has interpretability issues. New EU legislation, the General Data Protection Regulation, includes a [line](https://www.privacy-regulation.eu/en/r71.htm) about "the right ... to obtain an explanation of the decision reached", including by an algorithm.

Of course, there are many other good reasons to want the decisions of algorithms to be understandable and explainable. Interrogating why an algorithm makes the choices it does can highlight whether [it's working as intended](https://medium.com/@jrzech/what-are-radiological-deep-learning-models-actually-learning-f97a546c5b98), and, in some situations - such as public policy - transparency and interpretability may be essential ingredients of decision making.

But non-linear models are just not that easy to decompose into their fundamental components, they are - to an extent - a 'black box'. Ideally, we would be able to find the contribution of each input feature to the final prediction. In linear models, this is trivially achieved by the combination of the level of a feature and its regression coefficient. That is, for a linear model $f$ with features $x_{i\nu}$, $\nu \in \{1,p\}$ at a point $i$ such that

$$
{f}(x_{i\cdot})={f}(x_{i1},\ldots,x_{ip})=\beta_0+\beta_{1}x_{i1}+\ldots+\beta_{p}x_{ip}
$$

the contribution from feature $\nu$ is $x_{i\nu}\cdot\beta_\nu$. In non-linear models, it's not so simple.


### Shapley values

Game theory to the rescue. In 1953 Lloyd Shapley introduced values which effectively find, for a co-operative game, each player’s marginal contribution, averaged over every possible sequence in which the players could have been added to the group of players (Alvin Roth talks about it [here](https://voxeu.org/article/ideas-lloyd-shapley)). These are called Shapley values and, in a nutshell, they are the average expected marginal contribution of one player after all possible combinations of players have been considered.

This is exactly the kind of problem we want to solve to understand how different features contribute to a predicted value in a non-linear model, for instance in a machine learning. But it's easier to understand them in the linear case. The Shapley value for the linear model above would be, for feature $\nu$:

$$
\phi_{i\nu}({f})=\beta_{\nu}x_{i\nu}-E(\beta_{\nu}X_{\nu})=\beta_{\nu}x_{i\nu}-\beta_{\nu}E(X_{\nu})
$$

where no Einstein summation is implied. Summing over the different features gets back a number which is simply related to the overall prediction given by $f$,

$$
\sum_{\nu=1}^{p}\phi_{i\nu}({f})={f}(x_{i\cdot})-E({f}(X))
$$

The general equation for Shapley values looks more complicated, but is described by a function $g$ that assigns a real number to each coalition $S$, that is, to each subset of the combination of features, such that $g(S)$ represents the amount (of money or of utility) that coalition $S$ is able to transfer among its members in any way that they all agree to. Here it is:

$$
\phi_{i\nu}(f)=\sum_{S\subseteq\{x_{i1},\ldots,x_{ip}\}\setminus\{x_{i\nu}\}}\frac{|S|!\left(p-|S|-1\right)!}{p!}\underbrace{\left[g_{\left(S\cup\{x_{i\nu}\}\right)}\left(S\cup\{x_{i\nu}\}\right)-g_S(S)\right]}_{\text{Marginal contribution}}
$$

where

$$
g_{x_i}(S)=\int{f}(x_{i1},\ldots,x_{ip})d\mathbb{P}_{X_{i\cdot}\notin{}S}-E_X({f}(X))
$$


### Shapley values for machine learning

Shapley values have a number of nice properties which are both familiar from linear decompositions/linear models and highly desirable for machine learning models:

 - the Shapley value contributions sum to the difference between the full prediction and the average prediction (efficiency)

 - two features which contribute equally to any subset to which they're added have the same Shapley value (substitutability/symmetry)

- a feature which doesn't influence the predicted value has a Shapley value of 0 (dummy player)

These nice properties are not trivial for non-linear models, and Shapley values are the [only way to achieve them concurrently](http://www.lamsade.dauphine.fr/~airiau/Teaching/CoopGames/2011/coopgames-7[8up].pdf). They're also what suggest to me that Shapley values will become the primary interpretability method used and understood. There must be some catch, right?

There is. Which is why other methods, such as local surrogate models like [LIME](https://github.com/marcotcr/lime), are not going away anytime soon. If the factorials and sum over all combinations of input features in the equation didn't give it away, Shapley values are computationally expensive. As [this paper](https://link.springer.com/article/10.1007%2FBF01258278) points out, "every exact algorithm for the Shapley value requires an exponential number of operations". Oh dear.

The good news is that there are [good approximations](https://www.sciencedirect.com/science/article/pii/S0004370208000696?via%3Dihub) out there. The even better news is that there is a [Python library](https://github.com/slundberg/shap) called ```shap``` which implements a fast approximation method, is easy to use, and is even optimised for ```sklearn```. The paper behind this is [here](http://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions).

Not everyone is convinced by Shapley values but I think they could be particularly important as they have properties which are so clearly and neatly analogous to decompositions of linear models.

If you'd like to find out more about how Shapley values work, see these excellent explainer blog posts which I drew on heavily for this post:

- [One Feature Attribution Method to (Supposedly) Rule Them All: Shapley Values](https://towardsdatascience.com/one-feature-attribution-method-to-supposedly-rule-them-all-shapley-values-f3e04534983d)
- [Interpretable machine learning: Shapley Value Explanations](https://christophm.github.io/interpretable-ml-book/shapley.html)
- [Lloyd Shapley: A founding giant of game theory](https://voxeu.org/article/ideas-lloyd-shapley)
