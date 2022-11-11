from georetriever.utils import Lith
from georetriever.utils.geo_utils import get_random_lith


def test_lith_conversion():
    lith_obj = get_random_lith()
    lith_list = lith_obj.tolist()
    lith_obj = Lith.from_list(lith_list)

    assert lith_list == lith_obj.tolist()


if __name__ == "__main__":
    test_lith_conversion()
