import cv_engine
import numpy as np
import pytest
from cv_engine import build_result, summarize_led_frames


def frames_for_first_led(pattern: str) -> list[list[bool]]:
    first_led = [char == "1" for char in pattern]
    return [first_led, *[[False] * len(first_led) for _ in range(6)]]


@pytest.mark.parametrize("pattern", ["11111111", "11101111", "11100111"])
def test_mostly_on_led_is_solid_not_blinking(pattern):
    led_states, blink_leds = summarize_led_frames(frames_for_first_led(pattern))

    assert led_states == [True, False, False, False, False, False, False]
    assert blink_leds == []


def test_isolated_on_frame_is_not_blinking_or_solid():
    led_states, blink_leds = summarize_led_frames(frames_for_first_led("00010000"))

    assert led_states == [False, False, False, False, False, False, False]
    assert blink_leds == []


def test_tied_solid_led_counts_use_detection_strength():
    frames = [
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [False, False, False],
        [True, True, True],
        [True, True, True],
    ]
    strengths = [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
        [0.35, 0.37, 0.33],
        [0.57, 0.59, 0.57],
    ]

    led_states, blink_leds = summarize_led_frames(frames, strengths)

    assert led_states == [False, False, False, False, False, False, True]
    assert blink_leds == []


@pytest.mark.parametrize("pattern", ["11100011", "11000111", "10101010", "00111100"])
def test_repeated_on_off_patterns_are_blinking(pattern):
    led_states, blink_leds = summarize_led_frames(frames_for_first_led(pattern))

    assert led_states == [False, False, False, False, False, False, False]
    assert blink_leds == [1]


def led_state(level: int) -> list[bool]:
    states = [False] * 7
    states[level - 1] = True
    return states


@pytest.mark.parametrize("level", [1, 2, 3])
def test_chlorine_low_stable_leds_are_warning(level):
    result = build_result("chlorine", led_state(level), [])

    assert result == {
        "level": level,
        "mode": "dosing",
        "status": "warning",
        "diagnosis": "Below target",
    }


@pytest.mark.parametrize("level", [5, 6, 7])
def test_chlorine_high_stable_leds_are_warning(level):
    result = build_result("chlorine", led_state(level), [])

    assert result == {
        "level": level,
        "mode": "waiting",
        "status": "warning",
        "diagnosis": "Above target",
    }


@pytest.mark.parametrize("level", [1, 2, 3])
def test_ph_low_stable_leds_are_warning(level):
    result = build_result("ph", led_state(level), [])

    assert result == {
        "level": level,
        "mode": "waiting",
        "status": "warning",
        "diagnosis": "Below target",
    }


@pytest.mark.parametrize("level", [5, 6, 7])
def test_ph_high_stable_leds_are_warning(level):
    result = build_result("ph", led_state(level), [])

    assert result == {
        "level": level,
        "mode": "dosing",
        "status": "warning",
        "diagnosis": "Above target",
    }


@pytest.mark.parametrize("device", ["chlorine", "ph"])
def test_led_4_is_auto_for_both_devices(device):
    result = build_result(device, led_state(4), [])

    assert result == {
        "level": 4,
        "mode": "auto",
        "status": "ok",
        "diagnosis": "Auto mode",
    }


@pytest.mark.parametrize("device", ["chlorine", "ph"])
@pytest.mark.parametrize(
    ("blink_led", "diagnosis"),
    [(1, "Low (Standby)"), (4, "Standby mode"), (7, "High (Standby)")],
)
def test_single_blinking_led_is_standby_warning_for_both_devices(
    device, blink_led, diagnosis
):
    result = build_result(device, [False] * 7, [blink_led])

    assert result == {
        "level": blink_led if device == "chlorine" else None,
        "mode": "standby",
        "status": "warning",
        "diagnosis": diagnosis,
    }


@pytest.mark.parametrize("device", ["chlorine", "ph"])
def test_led_1_and_7_blinking_is_standby_warning(device):
    result = build_result(device, [False] * 7, [1, 7])

    assert result == {
        "level": 1 if device == "chlorine" else None,
        "mode": "standby",
        "status": "warning",
        "diagnosis": "Low (Standby)",
    }


@pytest.mark.parametrize("device", ["chlorine", "ph"])
def test_timeout_pattern_is_error(device):
    result = build_result(device, [False] * 7, [1, 2, 3, 5, 6, 7])

    assert result == {
        "level": None,
        "mode": "error",
        "status": "error",
        "diagnosis": "Time-out (dosing stopped)",
    }


def test_privacy_mask_timeout_shift_search_applies_to_chlorine():
    hsv_images = [np.zeros((500, 1300, 3), dtype=np.uint8) for _ in range(3)]
    shifted_rois = cv_engine.shifted_device_rois(
        cv_engine.PRIVACY_MASK_ROIS["chlorine"], 5, -3
    )

    for hsv in hsv_images:
        for led in cv_engine.TIMEOUT_BLINK_LEDS:
            x, y, w, h = shifted_rois[led - 1]
            hsv[y : y + h, x : x + w] = [0, 0, 255]

    assert cv_engine.detect_privacy_mask_timeout_with_shift_search(
        hsv_images, "chlorine"
    )
