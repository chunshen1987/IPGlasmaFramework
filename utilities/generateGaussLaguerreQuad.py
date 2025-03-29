from scipy.special import roots_laguerre

"""
We have the standard Gauss-Laguerre quadrature with weights
\\int_0^inf exp(-x) f(x) dx = sum_i w_i f(x_i),
where (x_i, w_i) are the roots and weights.

Generalize to more practical integrals,

\\int_0^inf exp(- alpha x) f(x) dx = sum_i w_i/alpha f(x_i/alpha),

where alpha is a slope parameter which controls how fast the expoential
decay is
"""


nPoints = 5
alpha = 20.

x, w = roots_laguerre(nPoints)
for i in range(nPoints):
    print(f"x_i = {x[i]/alpha:.6e}, w_i = {w[i]/alpha:.6e}")

