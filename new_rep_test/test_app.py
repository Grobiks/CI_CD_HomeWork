import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, calculation_history  # Импортируем calculation_history сразу

class CalculatorTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # Очищаем историю перед каждым тестом
        calculation_history.clear()  # Упрощаем вызов

    def test_home_page(self):
        """Тест главной страницы"""
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)
        # Используем более надежную проверку
        self.assertIn(b'<!DOCTYPE html>', r.data)

    def test_addition(self):
        """Тест сложения через API"""
        r = self.app.get('/api/calculate?a=5&b=3&operation=add')
        self.assertEqual(r.status_code, 200)  # Проверяем статус
        data = r.get_json()
        self.assertEqual(data['result'], 8.0)

    def test_subtraction(self):
        """Тест вычитания"""
        r = self.app.get('/api/calculate?a=10&b=4&operation=subtract')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 6.0)

    def test_multiplication(self):
        """Тест умножения"""
        r = self.app.get('/api/calculate?a=7&b=6&operation=multiply')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 42.0)

    def test_division(self):
        """Тест деления"""
        r = self.app.get('/api/calculate?a=15&b=3&operation=divide')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 5.0)

    def test_division_by_zero(self):
        """Тест деления на ноль"""
        r = self.app.get('/api/calculate?a=5&b=0&operation=divide')
        self.assertEqual(r.status_code, 400)  # Сначала статус
        data = r.get_json()
        self.assertIn('error', data)
        self.assertIn('Деление на ноль', data['error'])

    def test_power(self):
        """Тест возведения в степень"""
        r = self.app.get('/api/calculate?a=2&b=3&operation=power')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 8.0)

    def test_root(self):
        """Тест извлечения корня"""
        r = self.app.get('/api/calculate?a=8&b=3&operation=root')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertAlmostEqual(data['result'], 2.0, places=5)

    def test_post_calculation(self):
        """Тест POST запроса"""
        r = self.app.post('/api/calculate',
                         content_type='application/json',
                         data=json.dumps({'a': 10, 'b': 2, 'operation': 'multiply'}))
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 20.0)

    def test_history(self):
        """Тест истории вычислений"""
        # Сделаем несколько вычислений
        self.app.get('/api/calculate?a=1&b=2&operation=add')
        self.app.get('/api/calculate?a=3&b=4&operation=multiply')
        
        r = self.app.get('/api/history')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['history']), 2)
        # Проверяем операции
        operations = [item['operation'] for item in data['history']]
        self.assertIn('add', operations)
        self.assertIn('multiply', operations)

    def test_clear_history(self):
        """Тест очистки истории"""
        self.app.get('/api/calculate?a=1&b=2&operation=add')
        
        r = self.app.post('/api/history/clear')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['total'], 0)
        
        r = self.app.get('/api/history')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['total'], 0)
        self.assertEqual(len(data['history']), 0)

    def test_health_check(self):
        """Тест проверки работоспособности"""
        r = self.app.get('/health')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_invalid_operation(self):
        """Тест неверной операции"""
        r = self.app.get('/api/calculate?a=1&b=2&operation=invalid')
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertIn('error', data)

    def test_invalid_parameters(self):
        """Тест неверных параметров"""
        r = self.app.get('/api/calculate?a=not_a_number&b=2')
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertIn('error', data)

    def test_empty_parameters(self):
        """Тест с пустыми параметрами"""
        r = self.app.get('/api/calculate')
        self.assertEqual(r.status_code, 200)  # Должен использовать значения по умолчанию
        data = r.get_json()
        self.assertIn('result', data)

    def test_history_limit(self):
        """Тест ограничения истории"""
        # Добавим больше записей
        for i in range(15):
            self.app.get(f'/api/calculate?a={i}&b={i+1}&operation=add')
        
        r = self.app.get('/api/history?limit=5')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(len(data['history']), 5)
        self.assertEqual(data['total'], 15)

if __name__ == '__main__':
    unittest.main()