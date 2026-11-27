"""Model without data assimilation (translation of main.F90).

Usage: ``python main.py``
"""
from initialize import initialize
from integrate import integrate


def main() -> None:
    print('\n' + ' ' * 17 + '+++++ PDAF tutorial - online mode +++++\n')
    print(' ' * 9 + 'Tutorial: 2D model with 2 fields without parallelization')
    print('\n')
    initialize(use_pdaf=False)
    integrate()


if __name__ == '__main__':
    main()
