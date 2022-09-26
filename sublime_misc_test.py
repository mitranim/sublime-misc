def main():
    import unittest as ut
    import sublime_misc_util as u

    class test_main(ut.TestCase):
        def test_unquote(t):
            t.assertEqual(u.unquote(''), '')
            t.assertEqual(u.unquote('str'), 'str')
            t.assertEqual(u.unquote('\"str\"'), 'str')
            t.assertEqual(u.unquote('\"\"str\"\"'), '\"str\"')
            t.assertEqual(u.unquote('\"\'str\'\"'), '\'str\'')
            t.assertEqual(u.unquote('\'str\''), 'str')
            t.assertEqual(u.unquote('\'\'str\'\''), '\'str\'')
            t.assertEqual(u.unquote('`str`'), 'str')
            t.assertEqual(u.unquote('``str``'), '`str`')
            t.assertEqual(u.unquote('`\'str\'`'), '\'str\'')
            t.assertEqual(u.unquote('`\"str\"`'), '\"str\"')
            t.assertEqual(u.unquote('\"`str`\"'), '`str`')
            t.assertEqual(u.unquote('\'`str`\''), '`str`')

        def test_cycle_quote(t):
            t.assertEqual(u.cycle_quote(''), '``')
            t.assertEqual(u.cycle_quote('str'), '`str`')
            t.assertEqual(u.cycle_quote('\"str\"'), '`str`')
            t.assertEqual(u.cycle_quote('\"\"str\"\"'), '`\"str\"`')
            t.assertEqual(u.cycle_quote('\"\'str\'\"'), '`\'str\'`')
            t.assertEqual(u.cycle_quote('\'str\''), '"str"')
            t.assertEqual(u.cycle_quote('\'\'str\'\''), '"\'str\'"')
            t.assertEqual(u.cycle_quote('`str`'), '\'str\'')
            t.assertEqual(u.cycle_quote('``str``'), '\'`str`\'')
            t.assertEqual(u.cycle_quote('`\'str\'`'), '\'\'str\'\'')
            t.assertEqual(u.cycle_quote('`\"str\"`'), '\'\"str\"\'')
            t.assertEqual(u.cycle_quote('\"`str`\"'), '``str``')
            t.assertEqual(u.cycle_quote('\'`str`\''), '"`str`"')

    suite = ut.TestSuite()
    suite.addTests(ut.defaultTestLoader.loadTestsFromTestCase(test_main))
    ut.TextTestRunner().run(suite)

if __name__ == '__main__':
    main()
