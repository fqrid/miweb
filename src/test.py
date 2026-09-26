from main import calculator


def test_sum():
    calc = calculator()
    assert calc.sum(2, 2) == 4
