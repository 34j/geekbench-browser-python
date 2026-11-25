from geekbench_browser._breakdown import pick_result


def _c(id_, model, single, multi):
    return {"id": id_, "model": model, "single": single, "multi": multi}


def test_pick_result_closest_exact_name():
    candidates = [
        _c(1, "AMD Ryzen 9 9950X 4291 MHz (4 cores)", 2191, 6036),
        _c(2, "AMD Ryzen 9 9950X3D 4300 MHz (16 cores)", 3070, 26157),
        _c(3, "AMD Ryzen 9 9950X 4300 MHz (16 cores)", 3050, 25900),
        _c(4, "AMD Ryzen 9 9950X 4300 MHz (16 cores)", 3300, 21000),
    ]
    assert pick_result(candidates, "AMD Ryzen 9 9950X", 3070, 26157)["id"] == 3


def test_pick_result_none():
    candidates = [_c(2, "AMD Ryzen 9 9950X3D 4300 MHz (16 cores)", 3070, 26157)]
    assert pick_result(candidates, "AMD Ryzen 9 9950X", 3070, 26157) is None
    assert pick_result([], "AMD Ryzen 9 9950X", 3070, 26157) is None


def test_pick_result_ignores_other_core_counts():
    candidates = [
        _c(1, "AMD Ryzen 9 9950X 4291 MHz (4 cores)", 3067, 9001),
        _c(3, "AMD Ryzen 9 9950X 4300 MHz (16 cores)", 2800, 24000),
    ]
    assert pick_result(candidates, "AMD Ryzen 9 9950X", 3070, 26157, cores=16)["id"] == 3
    assert pick_result(candidates, "AMD Ryzen 9 9950X", 3070, 26157, cores=24) is None
