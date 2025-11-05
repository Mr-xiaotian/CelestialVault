from celestialvault.tools.NumberUtils import choose_square_container, redundancy_from_container
from celestialvault.tools.SampleGenerate import rand_strict_increasing_ints


def evaulate_choose_square_container():
    for n in rand_strict_increasing_ints(100, start=5, max_step=20):
        a, b, c  = choose_square_container(n, 0.7)
        test_c = redundancy_from_container(a*a, 0.7)
        print(f"n={n} -> 容器{a}, {b}, {c}, 利用率={n/a**2:.2%}")
        assert c == test_c


if __name__ == '__main__':
    evaulate_choose_square_container()
