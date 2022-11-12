from georetriever import GeoCutout


def test_data_retrieval():
    data = GeoCutout.open_dataset("test_data.nc")

    x_start = -1.5
    x_stop = -1
    y_start = 51
    y_stop = 50
    dx = 0.1
    dy = 0.1
    time = "2019-01-01"
    dt = "H"

    x = slice(*sorted([x_start, x_stop]))
    y = slice(*sorted([y_start, y_stop]))

    gc = GeoCutout(
        "first.netcdf",
        x=x,
        y=y,
        dx=dx,
        dy=dy,
        time=time,
        dt=dt,
    )

    gc.prepare(features=["temperature", "lithology"])

    assert data.equals(gc.data)


if __name__ == "__main__":
    test_data_retrieval()
