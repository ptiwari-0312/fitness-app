import pytest

from app.services.bmr_service import (
    calculate_bmr,
    calculate_tdee,
    calories_burned_from_steps,
    net_calories,
)


def test_bmr_male():
    # (10*70) + (6.25*175) - (5*25) + 5 = 1673.75
    assert calculate_bmr(70, 175, 25, "male") == pytest.approx(1673.75)


def test_bmr_female():
    # (10*60) + (6.25*165) - (5*30) - 161 = 1320.25
    assert calculate_bmr(60, 165, 30, "female") == pytest.approx(1320.25)


def test_bmr_gender_case_insensitive():
    assert calculate_bmr(70, 175, 25, "Male") == pytest.approx(calculate_bmr(70, 175, 25, "male"))


def test_tdee_sedentary():
    bmr = 1673.75
    assert calculate_tdee(bmr, "sedentary") == pytest.approx(bmr * 1.2)


def test_tdee_light():
    bmr = 1673.75
    assert calculate_tdee(bmr, "light") == pytest.approx(bmr * 1.375)


def test_tdee_moderate():
    bmr = 1673.75
    assert calculate_tdee(bmr, "moderate") == pytest.approx(bmr * 1.55)


def test_tdee_active():
    bmr = 1673.75
    assert calculate_tdee(bmr, "active") == pytest.approx(bmr * 1.725)


def test_tdee_very_active():
    bmr = 1673.75
    assert calculate_tdee(bmr, "very_active") == pytest.approx(bmr * 1.9)


def test_tdee_unknown_level_defaults_to_sedentary():
    bmr = 1500.0
    assert calculate_tdee(bmr, "unknown") == pytest.approx(bmr * 1.2)


def test_calories_burned_from_steps():
    # 10000 * 0.0005 * 70 = 350.0
    assert calories_burned_from_steps(10000, 70.0) == pytest.approx(350.0)


def test_calories_burned_zero_steps():
    assert calories_burned_from_steps(0, 70.0) == 0.0


def test_net_calories_surplus():
    assert net_calories(2000.0, 500.0) == pytest.approx(1500.0)


def test_net_calories_deficit():
    assert net_calories(1200.0, 1500.0) == pytest.approx(-300.0)


def test_net_calories_balanced():
    assert net_calories(2000.0, 2000.0) == pytest.approx(0.0)
