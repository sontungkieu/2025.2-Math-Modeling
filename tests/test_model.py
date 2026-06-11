import numpy as np
import pytest

from model import distance_to_front, enforce_no_overlap, simulate


def test_distance_to_front_normal_ordering():
    x = np.array([0.0, 2.0, 5.0])

    assert distance_to_front(0, x, L=10.0, N=3) == pytest.approx(2.0)
    assert distance_to_front(1, x, L=10.0, N=3) == pytest.approx(3.0)


def test_distance_to_front_across_periodic_boundary():
    x = np.array([0.5, 2.0, 8.0])

    assert distance_to_front(2, x, L=10.0, N=3) == pytest.approx(2.5)


def test_distance_to_front_uses_i_plus_one_for_explicit_bug_case():
    x = np.array([0.0, 1.95, 2.0])

    assert distance_to_front(1, x, L=10.0, N=3) == pytest.approx(0.05)


def test_enforce_no_overlap_restores_blocked_pedestrian():
    x_old = np.array([0.0, 2.0, 4.0])
    x_new = np.array([0.0, 3.75, 4.1])
    v_new = np.array([0.0, 1.0, 0.0])

    corrected_x, corrected_v = enforce_no_overlap(
        x_old=x_old,
        x_new=x_new,
        v_new=v_new,
        a=0.5,
        b=0.0,
        L=10.0,
        N=3,
    )

    assert corrected_x[1] == pytest.approx(x_old[1])
    assert corrected_v[1] == pytest.approx(0.0)


def test_enforce_no_overlap_cascades_to_following_pedestrian():
    x_old = np.array([0.0, 1.0, 3.0])
    x_new = np.array([0.8, 2.6, 3.0])
    v_new = np.array([1.0, 1.0, 0.0])

    corrected_x, corrected_v = enforce_no_overlap(
        x_old=x_old,
        x_new=x_new,
        v_new=v_new,
        a=0.75,
        b=0.0,
        L=10.0,
        N=3,
    )

    assert corrected_x[1] == pytest.approx(x_old[1])
    assert corrected_v[1] == pytest.approx(0.0)
    assert corrected_x[0] == pytest.approx(x_old[0])
    assert corrected_v[0] == pytest.approx(0.0)


def test_enforce_no_overlap_checks_pedestrian_zero_with_wrap():
    x_old = np.array([9.0, 0.5, 3.0])
    x_new = np.array([9.9, 0.1, 3.0])
    v_new = np.array([1.0, 0.0, 0.0])

    corrected_x, corrected_v = enforce_no_overlap(
        x_old=x_old,
        x_new=x_new,
        v_new=v_new,
        a=0.5,
        b=0.0,
        L=10.0,
        N=3,
    )

    assert corrected_x[0] == pytest.approx(x_old[0])
    assert corrected_v[0] == pytest.approx(0.0)


def test_simulate_seed_is_deterministic():
    kwargs = dict(
        N=3,
        L=10.0,
        dt=0.1,
        T_relax=2,
        T_measure=3,
        a=0.3,
        b=0.1,
        tau=1.0,
        v0_mean=1.0,
        v0_std=0.05,
        seed=123,
    )

    assert simulate(**kwargs) == pytest.approx(simulate(**kwargs))


def test_output_recording_uses_t_relax(tmp_path):
    output_file = tmp_path / "frames.csv"

    simulate(
        N=2,
        L=10.0,
        dt=0.1,
        T_relax=1,
        T_measure=1,
        a=0.3,
        b=0.0,
        tau=1.0,
        v0_mean=1.0,
        v0_std=0.0,
        output_file=str(output_file),
        seed=123,
    )

    assert output_file.read_text().strip()
