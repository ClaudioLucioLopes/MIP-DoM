# MIP-DoM

Dominance move (DoM) is a binary quality indicator that can be used in multi-objective and many-objective optimization to compare two solution sets obtained from different simulations. The DoM indicator can differentiate the sets for certain important features, such as convergence, spread, uniformity, and cardinality. DoM does not require any reference point or any representative Pareto solution set, and it has an intuitive and physical meaning, similar to the -indicator. It calculates the minimum total move of members of one set so that all elements in another set are to be dominated or identical to at least one member of the first set. 

This code is the implementation of our Mixed Integer Programming model to solve DoM, as described in [Analyzing Dominance Move (MIP-DoM) Indicator for Multi-and Many-objective Optimization](https://ieeexplore.ieee.org/document/9481257)

## Installation

To install Gurobi, please, follow this link: [Installing Gurobi Solver](http://matthiaswalter.org/intpm/Gurobi-Python3-Howto.pdf)

## Usage

```python
import MIPDoM as md
from numpy import genfromtxt


if __name__ == '__main__':
    P = genfromtxt('data/car1(A).txt', delimiter='\t')
    Q = genfromtxt('data/car1(B).txt', delimiter='\t')
    print(md.get_min_dom_mip_gurobi(P, Q, logprint=True, gapperc=1e-06))
    mip_dom_value, p_lines = md.get_min_dom_mip_gurobi(Q, P, logprint=True, gapperc=1e-06)
    assert(str(p_lines)=='{0: array([1.08769, 0.1    ]), 2: array([1.039693, 0.40902 ]), 3: array([0.966025, 0.55399 ]), 4: array([0.866044, 0.68778 ]), 5: array([0.68778, 0.80711]), 6: array([0.55399 , 0.966025]), 7: array([0.40902 , 1.039693]), 9: array([0.1    , 1.08769])}')
    assert(mip_dom_value==0.3515900000000003)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Citing This Work
You can cite this code as follows:

**C. L. d. V. Lopes, F. V. C. Martins, E. F. Wanner and K. Deb, "Analyzing Dominance Move (MIP-DoM) Indicator for Multi-and Many-objective Optimization," in IEEE Transactions on Evolutionary Computation, doi: 10.1109/TEVC.2021.3096669.**

### Bibtex

@ARTICLE{9481257,
  author={Lopes, Claudio Lucio do Val and Martins, Flávio Vinícius Cruzeiro and Wanner, Elizabeth Fialho and Deb, Kalyanmoy},
  journal={IEEE Transactions on Evolutionary Computation}, 
  title={Analyzing Dominance Move (MIP-DoM) Indicator for Multi-and Many-objective Optimization}, 
  year={2021},
  volume={},
  number={},
  pages={1-1},
  doi={10.1109/TEVC.2021.3096669}}



## License
[MIT](https://choosealicense.com/licenses/mit/)
