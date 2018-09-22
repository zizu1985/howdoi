#!/usr/bin/env python

"""Tests for Howdoi."""
import os
import unittest
import re
import subprocess
import ctypes
import sys

from howdoi import howdoi
"""
    Zapytanie pyquery do parsowania html
"""
from pyquery import PyQuery as pq

class HowdoiTestCase(unittest.TestCase):
    def call_howdoi(self, query):
        """ Crete parser. Parser musi ustawiac sparsowane argumenty jako atrybuty. Dlatego pojawia sie vars.
            vars zwraca slownik gdzie kluczem jest atrybutu. Vars
        """
        parser = howdoi.get_parser()
        args = vars(parser.parse_args(query.split(' ')))
        return howdoi.howdoi(args)

    def disable_network(self):
        """ Disable 2 nics required to disable network """
        if self._is_admin():
            completed = subprocess.run(args=['netsh', 'interface', 'set', 'interface', '"Wi-Fi"', 'disable'])
            print("Disable Wi-Fi ", completed.returncode)
            completed = subprocess.run(args=['netsh', 'interface', 'set', 'interface', '"Ethernet"', 'disable'])
            print("Disable Ethernet", completed.returncode)
        else:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", 'netsh', ' interface set interface "Wi-Fi" disable', None, 1)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", 'netsh', ' interface set interface "Ethernet" disable', None, 1)

    def enable_network(self):
        """ Enable 2 nics required to enable network """
        if self._is_admin():
            completed = subprocess.run(args=['netsh', 'interface', 'set', 'interface', '"Wi-Fi"', 'enable'])
            print("Enable Wi-Fi ", completed.returncode)
            completed = subprocess.run(args=['netsh', 'interface', 'set', 'interface', '"Ethernet"', 'enable'])
            print("Enable Ethernet", completed.returncode)
        else:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", 'netsh', ' interface set interface "Ethernet" enable', None, 1)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", 'netsh', ' interface set interface "Wi-Fi" enable', None, 1)

    def setUp(self):
        """ Create 3 list: 1st with proper queries in english, 2nd proper with , 3rd with wrong queries """
        self.queries = ['format date bash',
                        'print stack trace python',
                        'convert mp4 to animated gif',
                        'create tar archive',
                        'cat']
        self.pt_queries = ['abrir arquivo em python',
                           'enviar email em django',
                           'hello world em c']
        self.bad_queries = ['moe',
                            'mel']

    def _is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def tearDown(self):
        pass

    """
        Ten test tak na prawde testuje pobieranie elementow z listy z danej pozycji
    """
    def test_get_link_at_pos(self):
        self.assertEqual(howdoi.get_link_at_pos(['/questions/42/'], 1),
                         '/questions/42/')
        self.assertEqual(howdoi.get_link_at_pos(['/questions/42/'], 2),
                         '/questions/42/')
        self.assertEqual(howdoi.get_link_at_pos(['/howdoi', '/questions/42/'], 1),
                         '/howdoi')
        self.assertEqual(howdoi.get_link_at_pos(['/howdoi', '/questions/42/'], 2),
                         '/questions/42/')
        self.assertEqual(howdoi.get_link_at_pos(['/questions/42/', '/questions/142/'], 1),
                         '/questions/42/')

    def test_bad_queries(self):
            """ Bad query test with wrong answer """
            self.assertEqual(self.call_howdoi("Jak skompresowac plik?"), "Sorry, couldn't find any help with that topic\n", "Zle pytania daja dobra odpowiedz!")

    def test_answers(self):
        """
            Jezeli dostanie odpowiedz jakas to zwraca True. Jezeli nie potrafi to False.
            Jezelie ni moze sie podlaczyc to zwraca wyjatek.
        """
        for query in self.queries:
            self.assertTrue(self.call_howdoi(query))
        for query in self.bad_queries:
            self.assertTrue(self.call_howdoi(query))

        os.environ['HOWDOI_URL'] = 'pt.stackoverflow.com'
        for query in self.pt_queries:
            self.assertTrue(self.call_howdoi(query))

    def test_answers_bing(self):
        """ Test with using bing search engine.
            Search engine changed by set environment variable
        """
        os.environ['HOWDOI_SEARCH_ENGINE'] = 'bing'
        for query in self.queries:
            self.assertTrue(self.call_howdoi(query))
        for query in self.bad_queries:
            self.assertTrue(self.call_howdoi(query))

        os.environ['HOWDOI_URL'] = 'pt.stackoverflow.com'
        for query in self.pt_queries:
            self.assertTrue(self.call_howdoi(query))

        os.environ['HOWDOI_SEARCH_ENGINE'] = ''

    def test_answer_links_using_l_option(self):
        """
            Link do odpowiedzi zawsze zawiera questions.
            W zwiazku z tym sprawdzamy uzycie l i wynikowany URL pasuja do tego regexa.
        :return:
        """
        for query in self.queries:
            response = self.call_howdoi(query + ' -l')
            self.assertNotEqual(re.match('http.?://.*questions/\d.*', response, re.DOTALL), None)

    """ Test jest zbut prosty. Jezeli tak to zostawimy to testowanie -a i -l jest takie same.
        A opcja -a wyswietal wiecej.
        Poprawione. Jest to testowane w test_all_text.
        Ten test jest juz nie potrzebny.
    """
    def test_answer_links_using_all_option(self):
        for query in self.queries:
            response = self.call_howdoi(query + ' -a')
            self.assertNotEqual(re.match('.*Answer from http.?://.*', response, re.DOTALL), None)

    """
        Pozycja nie oznacza linka z listy linkow.
        Odpowiedz moze miec jeden link. A pozycje sa z tego linku.
        Test:
            Wybrac query: dobre i ktore ma conajmniej 2 pozycje.
            Pobrac odpowiedzi z pozycji 1 i z pozycji 2.
            Wyniki powinny byc rozne.
    """
    def test_position(self):
        query = self.queries[0]
        first_answer = self.call_howdoi(query)
        second_answer = self.call_howdoi(query + ' -p2')
        self.assertNotEqual(first_answer, second_answer)

    def test_default_position(self):
        """
            Test default value for position: 1
        :return:
        """
        query = self.queries[1]
        if query:
            first_answer = self.call_howdoi(query + " -p1")
            second_answer = self.call_howdoi(query)
            self.assertEqual(first_answer,second_answer)
        self.assertEqual(first_answer,second_answer,"Lack of proper query to test.")

    def test_all_text(self):
        """
            Testowanie opcji -a
            Daje ona co innego niz domyslna odpowiedz bez podania zadnej opcji.
            Test drugi sprawdza czy naglowek odpowiedzi dla -a jest ok.
        """
        query = self.queries[0]
        first_answer = self.call_howdoi(query)
        second_answer = self.call_howdoi(query + ' -a')
        self.assertNotEqual(first_answer, second_answer)
        self.assertNotEqual(re.match('.*Answer from http.?://.*', second_answer, re.DOTALL), None)

    def test_multiple_answers(self):
        """
            Test sprawdza ze wyswietlenie wiekszej liczby odpowiedzi
             jest dluzsze nie domyslne wyswietlenie pierwszej.
        :return:
        """
        " Dobre zapytanie."
        query = self.queries[0]
        " Odpowiedz do pierwszego zapytania. Domyslnie jedna odpowiedz"
        first_answer = self.call_howdoi(query)
        " 3 Odpowiedzi do zapytania. "
        second_answer = self.call_howdoi(query + ' -n3')
        " Nie moga byc takie same. "
        self.assertNotEqual(first_answer, second_answer)

    def test_unicode_answer(self):
        """
            Test dla 4 zapytan gdzie pytania zawieraja znaki Unicode.
            Poprawny wnyik -> odpowiedz zwraca true
        """
        assert self.call_howdoi('make a log scale d3')
        assert self.call_howdoi('python unittest -n3')
        assert self.call_howdoi('parse html regex -a')
        assert self.call_howdoi('delete remote git branch -a')


    def test_colorize(self):
        """
            Sprawdzenie czy flaga -c rzeczywiscie zwraca kolorki czy tez nie.
            Odpowiedz bez opcji nie moze zawierac koloru.
            Odpowiedz z opcja -c musi zawierac kolor.
            Sprawdznie czy odpowiedz jest kolorowa czy tez nie sprowadza sie do sprawdzenie czy odpowiedz zawiera znacznik [39;
                ktory wystepuja zawsze w kolorowej odpowiedzi.
        :return:
        """
        query = self.queries[0]
        normal = self.call_howdoi(query)
        colorized = self.call_howdoi('-c ' + query)
        self.assertTrue(normal.find('[39;') is -1)
        self.assertTrue(colorized.find('[39;') is not -1)

    def test_get_text_without_links(self):
        """
            Howdoi modul powinien zamienic htmla na wewnetrzny text pobierany z html za pomoca pyquery.
            Po co? Po to aby zamienic htmla ze stackoverflow na normalny text.
        """
        """ Jest sobie text html. Z samej rzeczy zawiera znaczniki htmlowe. """
        html = '''\n  <p>The halting problem is basically a\n  formal way of asking if you can tell\n  whether or not an arbitrary program\n  will eventually halt.</p>\n  \n  <p>In other words, can you write a\n  program called a halting oracle,\n  HaltingOracle(program, input), which\n  returns true if program(input) would\n  eventually halt, and which returns\n  false if it wouldn't?</p>\n  \n  <p>The answer is: no, you can't.</p>\n'''
        """ Za pomoca biblioteki pyquery parsujemy tego htmla """
        paragraph = pq(html)
        expected_output = '''The halting problem is basically a\n  formal way of asking if you can tell\n  whether or not an arbitrary program\n  will eventually halt.\n\n  \n  \nIn other words, can you write a\n  program called a halting oracle,\n  HaltingOracle(program, input), which\n  returns true if program(input) would\n  eventually halt, and which returns\n  false if it wouldn't?\n\n  \n  \nThe answer is: no, you can't.\n\n'''
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_text_with_one_link(self):
        """
            Html z pojedynczym linkiem powinien byc takze poprawnie sformatowany.
        :return:
        """
        html = '<p>It\'s a <a href="http://paulirish.com/2010/the-protocol-relative-url/">protocol-relative URL</a> (typically HTTP or HTTPS). So if I\'m on <code>http://example.org</code> and I link (or include an image, script, etc.) to <code>//example.com/1.png</code>, it goes to <code>http://example.com/1.png</code>. If I\'m on <code>https://example.org</code>, it goes to <code>https://example.com/1.png</code>.</p>'
        paragraph = pq(html)
        expected_output = "It's a [protocol-relative URL](http://paulirish.com/2010/the-protocol-relative-url/) (typically HTTP or HTTPS). So if I'm on http://example.org and I link (or include an image, script, etc.) to //example.com/1.png, it goes to http://example.com/1.png. If I'm on https://example.org, it goes to https://example.com/1.png."
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_text_with_multiple_links_test_one(self):
        html = 'Here\'s a quote from <a href="http://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style#Links" rel="nofollow noreferrer">wikipedia\'s manual of style</a> section on links (but see also <a href="http://en.wikipedia.org/wiki/Wikipedia:External_links" rel="nofollow noreferrer">their comprehensive page on External Links</a>)'
        paragraph = pq(html)
        expected_output = "Here's a quote from [wikipedia's manual of style](http://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style#Links) section on links (but see also [their comprehensive page on External Links](http://en.wikipedia.org/wiki/Wikipedia:External_links))"
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_text_with_multiple_links_test_two(self):
        html = 'For example, if I were to reference <a href="http://www.apple.com/" rel="nofollow noreferrer">apple.com</a> as the subject of a sentence - or to talk about <a href="http://www.apple.com/" rel="nofollow noreferrer">Apple\'s website</a> as the topic of conversation. This being different to perhaps recommendations for reading <a href="https://ux.stackexchange.com/q/14872/6046">our article about Apple\'s website</a>.'
        paragraph = pq(html)
        expected_output = "For example, if I were to reference [apple.com](http://www.apple.com/) as the subject of a sentence - or to talk about [Apple's website](http://www.apple.com/) as the topic of conversation. This being different to perhaps recommendations for reading [our article about Apple's website](https://ux.stackexchange.com/q/14872/6046)."
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_text_with_link_but_with_copy_duplicating_the_href(self):
        html ='<a href="https://github.com/jquery/jquery/blob/56136897f241db22560b58c3518578ca1453d5c7/src/manipulation.js#L451" rel="nofollow noreferrer">https://github.com/jquery/jquery/blob/56136897f241db22560b58c3518578ca1453d5c7/src/manipulation.js#L451</a>'
        paragraph = pq(html)
        expected_output = 'https://github.com/jquery/jquery/blob/56136897f241db22560b58c3518578ca1453d5c7/src/manipulation.js#L451'
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_text_with_a_link_but_copy_is_within_nested_div(self):
        html = 'If the function is from a source file available on the filesystem, then <a href="https://docs.python.org/3/library/inspect.html#inspect.getsource" rel="noreferrer"><code>inspect.getsource(foo)</code></a> might be of help:'
        paragraph = pq(html)
        expected_output = 'If the function is from a source file available on the filesystem, then [inspect.getsource(foo)](https://docs.python.org/3/library/inspect.html#inspect.getsource) might be of help:'
        actual_output = howdoi.get_text(paragraph)
        self.assertEqual(actual_output, expected_output)

    def test_get_questions(self):
        """
            Sprawdzenie odwrotnej operacji. Dla zadanej listy linkow zwroc liste pytan.
        :return:
        """
        links = ['https://stackoverflow.com/questions/tagged/cat', 'http://rads.stackoverflow.com/amzn/click/B007KAZ166', 'https://stackoverflow.com/questions/40108569/how-to-get-the-last-line-of-a-file-using-cat-command']
        expected_output = ['https://stackoverflow.com/questions/40108569/how-to-get-the-last-line-of-a-file-using-cat-command']
        actual_output = howdoi._get_questions(links)
        self.assertSequenceEqual(actual_output, expected_output)


class HowdoiTestCaseEnvProxies(unittest.TestCase):

    def setUp(self):
        self.temp_get_proxies = howdoi.getproxies

    def tearDown(self):
        howdoi.getproxies = self.temp_get_proxies

    def test_get_proxies1(self):
        def getproxies1():
            proxies = {'http': 'wwwproxy.company.com',
                       'https': 'wwwproxy.company.com',
                       'ftp': 'ftpproxy.company.com'}
            return proxies

        howdoi.getproxies = getproxies1
        filtered_proxies = howdoi.get_proxies()
        self.assertTrue('http://' in filtered_proxies['http'])
        self.assertTrue('http://' in filtered_proxies['https'])
        self.assertTrue('ftp' not in filtered_proxies.keys())


if __name__ == '__main__':
    unittest.main()
