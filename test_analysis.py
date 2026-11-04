"""python3 -m unittest test_analysis -v"""
import os
import tempfile
import unittest

import numpy as np

from analysis import add_kinematics, equation, fit, load_txt


class TestAnalysis(unittest.TestCase):
    def test_free_fall(self):
        t = np.linspace(0, 1, 21)
        y = 2.0 + 1.5 * t - 4.905 * t**2  # chute avec g = 9.81
        cols = add_kinematics({"t(s)": t, "x(m)": 0.5 * t, "y(m)": y})
        self.assertTrue(np.allclose(cols["vx(m/s)"], 0.5))
        # au centre, différences centrées exactes pour une parabole
        self.assertTrue(np.allclose(cols["vy(m/s)"][1:-1], 1.5 - 9.81 * t[1:-1]))
        coefs, r2 = fit("par", t, y)
        self.assertTrue(np.allclose(coefs, [-4.905, 1.5, 2.0]))
        self.assertAlmostEqual(r2, 1.0)
        a, _ = fit("aff", t[1:-1], cols["vy(m/s)"][1:-1])
        self.assertAlmostEqual(a[0], -9.81, places=6)

    def test_linear_through_origin(self):
        x = np.array([1.0, 2, 3])
        coefs, r2 = fit("lin", x, 2 * x)
        self.assertAlmostEqual(coefs[0], 2.0)
        self.assertIn("y = 2·x", equation("lin", coefs, r2))

    def test_too_few_points(self):
        with self.assertRaises(ValueError):
            fit("par", np.array([0.0, 1]), np.array([0.0, 1]))

    def test_load_avimeca_export_and_french_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            open(p, "w").write("t(s)\tx(m)\ty(m)\n0.0000\t0.1\t0.2\n0.0588\t0.15\t0.25\n")
            cols = load_txt(p)
            self.assertEqual(list(cols), ["t(s)", "x(m)", "y(m)"])
            self.assertAlmostEqual(cols["x(m)"][1], 0.15)
            q = os.path.join(d, "b.csv")
            open(q, "w").write("t;y\n0,5;1,25\nabc;def\n1,0;2,5\n")
            cols = load_txt(q)
            self.assertEqual(list(cols["y"]), [1.25, 2.5])


if __name__ == "__main__":
    unittest.main()
