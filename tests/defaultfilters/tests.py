# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal

from django.template.defaultfilters import *
from django.test import TestCase
from django.utils import six
from django.utils import unittest, translation
from django.utils.safestring import SafeData
from django.utils.encoding import python_2_unicode_compatible


class DefaultFiltersTests(TestCase):

    def test_floatformat(self):
        pos_inf = float(1e30000)
        self.assertEqual(floatformat(pos_inf), six.text_type(pos_inf))

        neg_inf = float(-1e30000)
        self.assertEqual(floatformat(neg_inf), six.text_type(neg_inf))

        nan = pos_inf / pos_inf
        self.assertEqual(floatformat(nan), six.text_type(nan))

        class FloatWrapper(object):
            def __init__(self, value):
                self.value = value
            def __float__(self):
                return self.value

        self.assertEqual(floatformat(FloatWrapper(11.000001), -2), '11.00')

        # Regression for #15789
        decimal_ctx = decimal.getcontext()
        old_prec, decimal_ctx.prec = decimal_ctx.prec, 2
        try:
            self.assertEqual(floatformat(1.2345, 2), '1.23')
            self.assertEqual(floatformat(15.2042, -3), '15.204')
            self.assertEqual(floatformat(1.2345, '2'), '1.23')
            self.assertEqual(floatformat(15.2042, '-3'), '15.204')
            self.assertEqual(floatformat(decimal.Decimal('1.2345'), 2), '1.23')
            self.assertEqual(floatformat(decimal.Decimal('15.2042'), -3), '15.204')
        finally:
            decimal_ctx.prec = old_prec


    def test_floatformat_py2_fail(self):
        self.assertEqual(floatformat(1.00000000000000015, 16), '1.0000000000000002')

    # The test above fails because of Python 2's float handling. Floats with
    # many zeroes after the decimal point should be passed in as another type
    # such as unicode or Decimal.
    if not six.PY3:
        test_floatformat_py2_fail = unittest.expectedFailure(test_floatformat_py2_fail)

    def test_rjust(self):
        self.assertEqual(ljust('test', 10), 'test      ')
        self.assertEqual(ljust('test', 3), 'test')
        self.assertEqual(rjust('test', 10), '      test')
        self.assertEqual(rjust('test', 3), 'test')

    def test_center(self):
        self.assertEqual(center('test', 6), ' test ')

    def test_cut(self):
        self.assertEqual(cut('a string to be mangled', 'a'),
                          ' string to be mngled')
        self.assertEqual(cut('a string to be mangled', 'ng'),
                          'a stri to be maled')
        self.assertEqual(cut('a string to be mangled', 'strings'),
                          'a string to be mangled')

    def test_force_escape(self):
        escaped = force_escape('<some html & special characters > here')
        self.assertEqual(
            escaped, '&lt;some html &amp; special characters &gt; here')
        self.assertTrue(isinstance(escaped, SafeData))
        self.assertEqual(
            force_escape('<some html & special characters > here ĐÅ€£'),
            '&lt;some html &amp; special characters &gt; here'\
            ' \u0110\xc5\u20ac\xa3')

    def test_linebreaks(self):
        self.assertEqual(linebreaks_filter('line 1'), '<p>line 1</p>')
        self.assertEqual(linebreaks_filter('line 1\nline 2'),
                          '<p>line 1<br />line 2</p>')
        self.assertEqual(linebreaks_filter('line 1\rline 2'),
                          '<p>line 1<br />line 2</p>')
        self.assertEqual(linebreaks_filter('line 1\r\nline 2'),
                          '<p>line 1<br />line 2</p>')

    def test_linebreaksbr(self):
        self.assertEqual(linebreaksbr('line 1\nline 2'),
                          'line 1<br />line 2')
        self.assertEqual(linebreaksbr('line 1\rline 2'),
                          'line 1<br />line 2')
        self.assertEqual(linebreaksbr('line 1\r\nline 2'),
                          'line 1<br />line 2')

    def test_removetags(self):
        self.assertEqual(removetags('some <b>html</b> with <script>alert'\
            '("You smell")</script> disallowed <img /> tags', 'script img'),
            'some <b>html</b> with alert("You smell") disallowed  tags')
        self.assertEqual(striptags('some <b>html</b> with <script>alert'\
            '("You smell")</script> disallowed <img /> tags'),
            'some html with alert("You smell") disallowed  tags')

    def test_dictsort(self):
        sorted_dicts = dictsort([{'age': 23, 'name': 'Barbara-Ann'},
                                 {'age': 63, 'name': 'Ra Ra Rasputin'},
                                 {'name': 'Jonny B Goode', 'age': 18}], 'age')

        self.assertEqual([sorted(dict.items()) for dict in sorted_dicts],
            [[('age', 18), ('name', 'Jonny B Goode')],
             [('age', 23), ('name', 'Barbara-Ann')],
             [('age', 63), ('name', 'Ra Ra Rasputin')]])

        # If it gets passed a list of something else different from
        # dictionaries it should fail silently
        self.assertEqual(dictsort([1, 2, 3], 'age'), '')
        self.assertEqual(dictsort('Hello!', 'age'), '')
        self.assertEqual(dictsort({'a': 1}, 'age'), '')
        self.assertEqual(dictsort(1, 'age'), '')

    def test_dictsortreversed(self):
        sorted_dicts = dictsortreversed([{'age': 23, 'name': 'Barbara-Ann'},
                                         {'age': 63, 'name': 'Ra Ra Rasputin'},
                                         {'name': 'Jonny B Goode', 'age': 18}],
                                        'age')

        self.assertEqual([sorted(dict.items()) for dict in sorted_dicts],
            [[('age', 63), ('name', 'Ra Ra Rasputin')],
             [('age', 23), ('name', 'Barbara-Ann')],
             [('age', 18), ('name', 'Jonny B Goode')]])

        # If it gets passed a list of something else different from
        # dictionaries it should fail silently
        self.assertEqual(dictsortreversed([1, 2, 3], 'age'), '')
        self.assertEqual(dictsortreversed('Hello!', 'age'), '')
        self.assertEqual(dictsortreversed({'a': 1}, 'age'), '')
        self.assertEqual(dictsortreversed(1, 'age'), '')

    def test_first(self):
        self.assertEqual(first([0,1,2]), 0)
        self.assertEqual(first(''), '')
        self.assertEqual(first('test'), 't')

    def test_join(self):
        self.assertEqual(join([0,1,2], 'glue'), '0glue1glue2')

    def test_length(self):
        self.assertEqual(length('1234'), 4)
        self.assertEqual(length([1,2,3,4]), 4)
        self.assertEqual(length_is([], 0), True)
        self.assertEqual(length_is([], 1), False)
        self.assertEqual(length_is('a', 1), True)
        self.assertEqual(length_is('a', 10), False)

    def test_slice(self):
        self.assertEqual(slice_filter('abcdefg', '0'), '')
        self.assertEqual(slice_filter('abcdefg', '1'), 'a')
        self.assertEqual(slice_filter('abcdefg', '-1'), 'abcdef')
        self.assertEqual(slice_filter('abcdefg', '1:2'), 'b')
        self.assertEqual(slice_filter('abcdefg', '1:3'), 'bc')
        self.assertEqual(slice_filter('abcdefg', '0::2'), 'aceg')

    def test_unordered_list(self):
        self.assertEqual(unordered_list(['item 1', 'item 2']),
            '\t<li>item 1</li>\n\t<li>item 2</li>')
        self.assertEqual(unordered_list(['item 1', ['item 1.1']]),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</ul>\n\t</li>')

        self.assertEqual(
            unordered_list(['item 1', ['item 1.1', 'item1.2'], 'item 2']),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t\t<li>item1.2'\
            '</li>\n\t</ul>\n\t</li>\n\t<li>item 2</li>')

        self.assertEqual(
            unordered_list(['item 1', ['item 1.1', ['item 1.1.1',
                                                      ['item 1.1.1.1']]]]),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1\n\t\t<ul>\n\t\t\t<li>'\
            'item 1.1.1\n\t\t\t<ul>\n\t\t\t\t<li>item 1.1.1.1</li>\n\t\t\t'\
            '</ul>\n\t\t\t</li>\n\t\t</ul>\n\t\t</li>\n\t</ul>\n\t</li>')

        self.assertEqual(unordered_list(
            ['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]),
            '\t<li>States\n\t<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>'\
            'Lawrence</li>\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>'\
            '\n\t\t<li>Illinois</li>\n\t</ul>\n\t</li>')

        @python_2_unicode_compatible
        class ULItem(object):
            def __init__(self, title):
              self.title = title
            def __str__(self):
                return 'ulitem-%s' % str(self.title)

        a = ULItem('a')
        b = ULItem('b')
        self.assertEqual(unordered_list([a,b]),
                          '\t<li>ulitem-a</li>\n\t<li>ulitem-b</li>')

        # Old format for unordered lists should still work
        self.assertEqual(unordered_list(['item 1', []]), '\t<li>item 1</li>')

        self.assertEqual(unordered_list(['item 1', [['item 1.1', []]]]),
            '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1</li>\n\t</ul>\n\t</li>')

        self.assertEqual(unordered_list(['item 1', [['item 1.1', []],
            ['item 1.2', []]]]), '\t<li>item 1\n\t<ul>\n\t\t<li>item 1.1'\
            '</li>\n\t\t<li>item 1.2</li>\n\t</ul>\n\t</li>')

        self.assertEqual(unordered_list(['States', [['Kansas', [['Lawrence',
            []], ['Topeka', []]]], ['Illinois', []]]]), '\t<li>States\n\t'\
            '<ul>\n\t\t<li>Kansas\n\t\t<ul>\n\t\t\t<li>Lawrence</li>'\
            '\n\t\t\t<li>Topeka</li>\n\t\t</ul>\n\t\t</li>\n\t\t<li>'\
            'Illinois</li>\n\t</ul>\n\t</li>')

    def test_add(self):
        self.assertEqual(add('1', '2'), 3)

    def test_get_digit(self):
        self.assertEqual(get_digit(123, 1), 3)
        self.assertEqual(get_digit(123, 2), 2)
        self.assertEqual(get_digit(123, 3), 1)
        self.assertEqual(get_digit(123, 4), 0)
        self.assertEqual(get_digit(123, 0), 123)
        self.assertEqual(get_digit('xyz', 0), 'xyz')

    def test_date(self):
        # real testing of date() is in dateformat.py
        self.assertEqual(date(datetime.datetime(2005, 12, 29), "d F Y"),
                          '29 December 2005')
        self.assertEqual(date(datetime.datetime(2005, 12, 29), r'jS \o\f F'),
                          '29th of December')

    def test_time(self):
        # real testing of time() is done in dateformat.py
        self.assertEqual(time(datetime.time(13), "h"), '01')
        self.assertEqual(time(datetime.time(0), "h"), '12')

    def test_timesince(self):
        # real testing is done in timesince.py, where we can provide our own 'now'
        self.assertEqual(
            timesince_filter(datetime.datetime.now() - datetime.timedelta(1)),
            '1 day')

        self.assertEqual(
            timesince_filter(datetime.datetime(2005, 12, 29),
                             datetime.datetime(2005, 12, 30)),
            '1 day')

    def test_timeuntil(self):
        self.assertEqual(
            timeuntil_filter(datetime.datetime.now() + datetime.timedelta(1, 1)),
            '1 day')

        self.assertEqual(
            timeuntil_filter(datetime.datetime(2005, 12, 30),
                             datetime.datetime(2005, 12, 29)),
            '1 day')

    def test_default(self):
        self.assertEqual(default("val", "default"), 'val')
        self.assertEqual(default(None, "default"), 'default')
        self.assertEqual(default('', "default"), 'default')

    def test_if_none(self):
        self.assertEqual(default_if_none("val", "default"), 'val')
        self.assertEqual(default_if_none(None, "default"), 'default')
        self.assertEqual(default_if_none('', "default"), '')

    def test_divisibleby(self):
        self.assertEqual(divisibleby(4, 2), True)
        self.assertEqual(divisibleby(4, 3), False)

    def test_yesno(self):
        self.assertEqual(yesno(True), 'yes')
        self.assertEqual(yesno(False), 'no')
        self.assertEqual(yesno(None), 'maybe')
        self.assertEqual(yesno(True, 'certainly,get out of town,perhaps'),
                          'certainly')
        self.assertEqual(yesno(False, 'certainly,get out of town,perhaps'),
                          'get out of town')
        self.assertEqual(yesno(None, 'certainly,get out of town,perhaps'),
                          'perhaps')
        self.assertEqual(yesno(None, 'certainly,get out of town'),
                          'get out of town')

    def test_filesizeformat(self):
        self.assertEqual(filesizeformat(1023), '1023 bytes')
        self.assertEqual(filesizeformat(1024), '1.0 KB')
        self.assertEqual(filesizeformat(10*1024), '10.0 KB')
        self.assertEqual(filesizeformat(1024*1024-1), '1024.0 KB')
        self.assertEqual(filesizeformat(1024*1024), '1.0 MB')
        self.assertEqual(filesizeformat(1024*1024*50), '50.0 MB')
        self.assertEqual(filesizeformat(1024*1024*1024-1), '1024.0 MB')
        self.assertEqual(filesizeformat(1024*1024*1024), '1.0 GB')
        self.assertEqual(filesizeformat(1024*1024*1024*1024), '1.0 TB')
        self.assertEqual(filesizeformat(1024*1024*1024*1024*1024), '1.0 PB')
        self.assertEqual(filesizeformat(1024*1024*1024*1024*1024*2000),
                          '2000.0 PB')
        self.assertEqual(filesizeformat(complex(1,-1)), '0 bytes')
        self.assertEqual(filesizeformat(""), '0 bytes')
        self.assertEqual(filesizeformat("\N{GREEK SMALL LETTER ALPHA}"),
                          '0 bytes')

    def test_localized_filesizeformat(self):
        with self.settings(USE_L10N=True):
            with translation.override('de', deactivate=True):
                self.assertEqual(filesizeformat(1023), '1023 Bytes')
                self.assertEqual(filesizeformat(1024), '1,0 KB')
                self.assertEqual(filesizeformat(10*1024), '10,0 KB')
                self.assertEqual(filesizeformat(1024*1024-1), '1024,0 KB')
                self.assertEqual(filesizeformat(1024*1024), '1,0 MB')
                self.assertEqual(filesizeformat(1024*1024*50), '50,0 MB')
                self.assertEqual(filesizeformat(1024*1024*1024-1), '1024,0 MB')
                self.assertEqual(filesizeformat(1024*1024*1024), '1,0 GB')
                self.assertEqual(filesizeformat(1024*1024*1024*1024), '1,0 TB')
                self.assertEqual(filesizeformat(1024*1024*1024*1024*1024),
                                  '1,0 PB')
                self.assertEqual(filesizeformat(1024*1024*1024*1024*1024*2000),
                                  '2000,0 PB')
                self.assertEqual(filesizeformat(complex(1,-1)), '0 Bytes')
                self.assertEqual(filesizeformat(""), '0 Bytes')
                self.assertEqual(filesizeformat("\N{GREEK SMALL LETTER ALPHA}"),
                                  '0 Bytes')

    def test_pluralize(self):
        self.assertEqual(pluralize(1), '')
        self.assertEqual(pluralize(0), 's')
        self.assertEqual(pluralize(2), 's')
        self.assertEqual(pluralize([1]), '')
        self.assertEqual(pluralize([]), 's')
        self.assertEqual(pluralize([1,2,3]), 's')
        self.assertEqual(pluralize(1,'es'), '')
        self.assertEqual(pluralize(0,'es'), 'es')
        self.assertEqual(pluralize(2,'es'), 'es')
        self.assertEqual(pluralize(1,'y,ies'), 'y')
        self.assertEqual(pluralize(0,'y,ies'), 'ies')
        self.assertEqual(pluralize(2,'y,ies'), 'ies')
        self.assertEqual(pluralize(0,'y,ies,error'), '')

    def test_phone2numeric(self):
        self.assertEqual(phone2numeric_filter('0800 flowers'), '0800 3569377')

    def test_non_string_input(self):
        # Filters shouldn't break if passed non-strings
        self.assertEqual(addslashes(123), '123')
        self.assertEqual(linenumbers(123), '1. 123')
        self.assertEqual(lower(123), '123')
        self.assertEqual(make_list(123), ['1', '2', '3'])
        self.assertEqual(slugify(123), '123')
        self.assertEqual(title(123), '123')
        self.assertEqual(truncatewords(123, 2), '123')
        self.assertEqual(upper(123), '123')
        self.assertEqual(urlencode(123), '123')
        self.assertEqual(urlize(123), '123')
        self.assertEqual(urlizetrunc(123, 1), '123')
        self.assertEqual(wordcount(123), 1)
        self.assertEqual(wordwrap(123, 2), '123')
        self.assertEqual(ljust('123', 4), '123 ')
        self.assertEqual(rjust('123', 4), ' 123')
        self.assertEqual(center('123', 5), ' 123 ')
        self.assertEqual(center('123', 6), ' 123  ')
        self.assertEqual(cut(123, '2'), '13')
        self.assertEqual(escape(123), '123')
        self.assertEqual(linebreaks_filter(123), '<p>123</p>')
        self.assertEqual(linebreaksbr(123), '123')
        self.assertEqual(removetags(123, 'a'), '123')
        self.assertEqual(striptags(123), '123')

