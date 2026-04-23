import glob
import os

import pytest
from cv_engine import analyze_burst


def get_fixture_dir(burst_folder):
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    return os.path.join(backend_root, "tests/fixtures", burst_folder)


@pytest.mark.parametrize(
    "burst_folder,expected_chlorine_blinking,expected_status,expected_diagnosis,expected_ph_diagnosis,expected_ph_level,expected_chlorine_level,expected_ph_led_states,expected_chlorine_led_states,expected_ph_blinking",
    [
        (
            "burst_5_light_off",
            [2],  # Expected chlorine blinking
            "warning",  # Expected status
            "Low (Standby)",  # Expected diagnosis
            "Auto mode",  # Expected PH diagnosis
            4,  # Expected PH level
            2,  # Expected Chlorine level
            [False, False, False, True, False, False, False],  # Expected PH led_states
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],  # Expected Chlorine led_states
            [],  # Expected PH blinking
        ),
        (
            "burst_6_light_off",
            [1],  # Expected chlorine blinking
            "warning",  # Expected status
            "Low (Standby)",  # Expected diagnosis
            "Auto mode",  # Expected PH diagnosis
            4,  # Expected PH level
            1,  # Expected Chlorine level
            [False, False, False, True, False, False, False],  # Expected PH led_states
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],  # Expected Chlorine led_states
            [],  # Expected PH blinking
        ),
        (
            "burst_7_light_off",
            [],  # Expected chlorine blinking
            "ok",  # Expected status
            "Auto mode",  # Expected diagnosis
            "High (Standby)",  # Expected PH diagnosis
            5,  # Expected PH level
            4,  # Expected Chlorine level
            [False, False, False, False, True, False, False],  # Expected PH led_states
            [
                False,
                False,
                False,
                True,
                False,
                False,
                False,
            ],  # Expected Chlorine led_states
            [7],  # Expected PH blinking
        ),
    ],
)
def test_cv_logic_fixtures(
    burst_folder,
    expected_chlorine_blinking,
    expected_status,
    expected_diagnosis,
    expected_ph_diagnosis,
    expected_ph_level,
    expected_chlorine_level,
    expected_ph_led_states,
    expected_chlorine_led_states,
    expected_ph_blinking,
):
    fixture_dir = get_fixture_dir(burst_folder)
    image_paths = sorted(glob.glob(os.path.join(fixture_dir, "*.jpg")))

    if not image_paths:
        pytest.fail(f"No images found in {fixture_dir}")

    images_bytes = []
    for path in image_paths:
        with open(path, "rb") as f:
            images_bytes.append(f.read())

    result = analyze_burst(images_bytes)

    chl = result["chlorine"]
    assert chl["status"] == expected_status
    assert chl["diagnosis"] == expected_diagnosis
    assert chl["level"] == expected_chlorine_level

    ph = result["ph"]
    assert ph["diagnosis"] == expected_ph_diagnosis
    assert ph["level"] == expected_ph_level

    # Assertions for PH led_states and blinking
    assert ph["led_states"] == expected_ph_led_states
    assert ph["blinking"] == expected_ph_blinking

    # Assertions for Chlorine led_states
    assert chl["led_states"] == expected_chlorine_led_states

    # Assertions for Chlorine blinking
    assert chl["blinking"] == expected_chlorine_blinking
