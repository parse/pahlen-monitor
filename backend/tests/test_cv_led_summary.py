import pytest
from cv_engine import summarize_led_frames


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


@pytest.mark.parametrize("pattern", ["11100011", "11000111", "10101010", "00111100"])
def test_repeated_on_off_patterns_are_blinking(pattern):
    led_states, blink_leds = summarize_led_frames(frames_for_first_led(pattern))

    assert led_states == [False, False, False, False, False, False, False]
    assert blink_leds == [1]
