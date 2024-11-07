import unittest

class TestMathOperations(unittest.TestCase):

    def test_addition(self):
        test_cases = [
            (1, 1, 2),
            (2, 2, 5),
            (3, 3, 6),
            (4, 5, 10)
        ]

        for a, b, expected in test_cases:
            with self.subTest(msg=f"Comparing {a} + {b} with {expected}", a=a, b=b, expected=expected):
                self.assertEqual(a + b, expected)

if __name__ == '__main__':
    unittest.main()

