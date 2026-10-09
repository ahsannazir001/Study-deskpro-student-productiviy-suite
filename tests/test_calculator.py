"""Tests for calculator safe parser."""

import pytest
from app.gui.calculator import safe_eval, CalcError, format_result


class TestCalculator:
    def test_addition(self):
        assert safe_eval("2+3") == 5

    def test_subtraction(self):
        assert safe_eval("10-4") == 6

    def test_multiplication(self):
        assert safe_eval("6*7") == 42

    def test_division(self):
        assert safe_eval("10/2") == 5

    def test_division_by_zero(self):
        with pytest.raises(CalcError, match="Division by zero"):
            safe_eval("1/0")

    def test_modulo(self):
        assert safe_eval("10%3") == 1

    def test_modulo_by_zero(self):
        with pytest.raises(CalcError, match="Modulo by zero"):
            safe_eval("10%0")

    def test_parentheses(self):
        assert safe_eval("(2+3)*4") == 20

    def test_nested_parentheses(self):
        assert safe_eval("((2+3)*2)") == 10

    def test_decimal(self):
        assert safe_eval("3.5+2.5") == 6.0

    def test_unary_minus(self):
        assert safe_eval("-5+10") == 5

    def test_complex_expression(self):
        assert safe_eval("2+3*4") == 14

    def test_spaces(self):
        assert safe_eval(" 2 + 3 * 4 ") == 14

    def test_empty_expression(self):
        with pytest.raises(CalcError):
            safe_eval("")

    def test_invalid_expression(self):
        with pytest.raises(CalcError):
            safe_eval("2++")

    def test_missing_paren(self):
        with pytest.raises(CalcError):
            safe_eval("(2+3")

    def test_format_result_int(self):
        assert format_result(5.0) == "5"

    def test_format_result_float(self):
        assert format_result(3.14) == "3.14"

    def test_percentage_like(self):
        assert safe_eval("100*0.1") == 10.0