from wbcd_task1.planning.motion.search_pattern import generate_cross_search_pattern


def test_cross_search_pattern_radius():
    points = generate_cross_search_pattern(step_m=0.001, radius_m=0.003)
    assert points[0] == (0.0, 0.0, 0.0)
    assert len(points) == 13
    assert (0.003, 0.0, 0.0) in points
    assert (0.0, -0.003, 0.0) in points
