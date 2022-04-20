import MIPDoM as md
from numpy import genfromtxt


if __name__ == '__main__':
    P = genfromtxt('data/car1(A).txt', delimiter='\t')
    Q = genfromtxt('data/car1(B).txt', delimiter='\t')
    print(md.get_min_dom_mip_gurobi(P, Q, logprint=True, gapperc=1e-06))
    mip_dom_value, p_lines = md.get_min_dom_mip_gurobi(Q, P, logprint=True, gapperc=1e-06)
    assert(str(p_lines)=='{0: array([1.08769, 0.1    ]), 2: array([1.039693, 0.40902 ]), 3: array([0.966025, 0.55399 ]), 4: array([0.866044, 0.68778 ]), 5: array([0.68778, 0.80711]), 6: array([0.55399 , 0.966025]), 7: array([0.40902 , 1.039693]), 9: array([0.1    , 1.08769])}')
    assert(mip_dom_value==0.3515900000000003)
