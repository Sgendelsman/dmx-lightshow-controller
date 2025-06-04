import math

# from_val -> [0, 255]
# to_val -> [0, 255]
# t -> [0, 1]
# Returns a linear approximation of the val based on t.
def linear_fade(from_val, to_val, t):
    linear_approximation = int(from_val + (to_val - from_val) * t)
    return min(255, linear_approximation)

# from_val -> [0, 255]
# to_val -> [0, 255]
# t -> [0, 1]
# Returns a quadratic approximation of the val based on t (weighted to early values of t).
def quadratic_fade(from_val, to_val, t):
    quadratic_approximation = int(from_val + (to_val - from_val) * (1 - (1-t)**2))
    return min(255, quadratic_approximation)
