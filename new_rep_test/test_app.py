import unittest
import json
import sys
import os
import math 
import random

sys.path.insert(0, os.path.dirname(__file__))

from app import app, calculation_history, generate_pro_modal_data

class CalculatorTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.app = app.test_client()
        # Очищаем историю перед каждым тестом
        calculation_history.clear()
        # Сбрасываем сессию для каждого теста
        with self.app.session_transaction() as session:
            session.clear()

    def test_home_page(self):
        """Тест главной страницы"""
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', r.data)

    def test_home_page_with_pro_modal(self):
        """Тест главной страницы с проверкой передачи данных для PRO модалки"""
        r = self.app.get('/')
        self.assertEqual(r.status_code, 200)
        
        # Проверяем что страница загружается (базовая проверка)
        self.assertIn(b'<title>', r.data)
        
        # При первом заходе должна быть возможность показа модалки
        # (проверяем через наличие session данных)

    def test_generate_pro_modal_data(self):
        """Тест генерации данных для PRO модалки"""
        data = generate_pro_modal_data()
        
        # Проверяем что все необходимые поля есть
        self.assertIn('pro_price', data)
        self.assertIn('fake_reviews', data)
        self.assertIn('already_sold', data)
        self.assertIn('satisfaction_rate', data)
        self.assertIn('current_time', data)
        self.assertIn('fake_timer', data)
        
        # Проверяем типы данных
        self.assertIsInstance(data['pro_price'], str)
        self.assertIsInstance(data['fake_reviews'], list)
        self.assertIsInstance(data['already_sold'], int)
        self.assertIsInstance(data['satisfaction_rate'], int)
        self.assertIsInstance(data['fake_timer'], int)
        
        # Проверяем диапазоны
        self.assertGreaterEqual(data['already_sold'], 1500)
        self.assertLessEqual(data['already_sold'], 10000)
        self.assertGreaterEqual(data['satisfaction_rate'], 96)
        self.assertLessEqual(data['satisfaction_rate'], 100)
        self.assertGreaterEqual(data['fake_timer'], 5)
        self.assertLessEqual(data['fake_timer'], 15)

    # Бинарные операции
    def test_addition(self):
        """Тест сложения через API"""
        r = self.app.get('/api/calculate?a=5&b=3&operation=add')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 8.0)
        self.assertIn('b', data)
        self.assertEqual(data['b'], 3.0)
        self.assertIn('pro_activated', data)  # Новое поле

    def test_subtraction(self):
        """Тест вычитания"""
        r = self.app.get('/api/calculate?a=10&b=4&operation=subtract')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 6.0)
        self.assertIn('b', data)
        self.assertIn('pro_activated', data)

    def test_multiplication(self):
        """Тест умножения"""
        r = self.app.get('/api/calculate?a=7&b=6&operation=multiply')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 42.0)
        self.assertIn('b', data)
        self.assertIn('pro_activated', data)

    def test_division(self):
        """Тест деления"""
        r = self.app.get('/api/calculate?a=15&b=3&operation=divide')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 5.0)
        self.assertIn('b', data)
        self.assertIn('pro_activated', data)

    def test_division_by_zero(self):
        """Тест деления на ноль"""
        r = self.app.get('/api/calculate?a=5&b=0&operation=divide')
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertIn('error', data)
        self.assertIn('Деление на ноль', data['error'])

    def test_power(self):
        """Тест возведения в степень"""
        r = self.app.get('/api/calculate?a=2&b=3&operation=power')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 8.0)
        self.assertIn('b', data)
        self.assertIn('pro_activated', data)

    def test_root(self):
        """Тест извлечения корня n-ной степени"""
        r = self.app.get('/api/calculate?a=8&b=3&operation=root')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertAlmostEqual(data['result'], 2.0, places=5)
        self.assertIn('b', data)
        self.assertEqual(data['b'], 3.0)
        self.assertIn('pro_activated', data)

    # Унарные операции (требуют только a)
    def test_square_root(self):
        """Тест квадратного корня"""
        r = self.app.get('/api/calculate?a=16&operation=sqrt')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 4.0)
        self.assertNotIn('b', data)  # b не должно быть в ответе для унарных операций
        self.assertIn('pro_activated', data)

    def test_square(self):
        """Тест возведения в квадрат"""
        r = self.app.get('/api/calculate?a=5&operation=square')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 25.0)
        self.assertNotIn('b', data)
        self.assertIn('pro_activated', data)

    def test_cube(self):
        """Тест возведения в куб"""
        r = self.app.get('/api/calculate?a=3&operation=cube')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 27.0)
        self.assertNotIn('b', data)
        self.assertIn('pro_activated', data)

    def test_square_root_negative(self):
        """Тест квадратного корня из отрицательного числа"""
        r = self.app.get('/api/calculate?a=-16&operation=sqrt')
        self.assertEqual(r.status_code, 200)  # Возвращает float('nan')
        data = r.get_json()
        self.assertTrue(math.isnan(data['result']))
        self.assertIn('pro_activated', data)

    # POST запросы
    def test_post_calculation_binary(self):
        """Тест POST запроса для бинарной операции"""
        r = self.app.post('/api/calculate',
                         content_type='application/json',
                         data=json.dumps({'a': 10, 'b': 2, 'operation': 'multiply'}))
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 20.0)
        self.assertIn('b', data)
        self.assertIn('pro_activated', data)

    def test_post_calculation_unary(self):
        """Тест POST запроса для унарной операции"""
        r = self.app.post('/api/calculate',
                         content_type='application/json',
                         data=json.dumps({'a': 9, 'operation': 'sqrt'}))
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 3.0)
        self.assertNotIn('b', data)
        self.assertIn('pro_activated', data)

    # История вычислений
    def test_history(self):
        """Тест истории вычислений"""
        # Сделаем несколько вычислений
        self.app.get('/api/calculate?a=1&b=2&operation=add')
        self.app.get('/api/calculate?a=3&operation=square')  # унарная операция
        
        r = self.app.get('/api/history')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['history']), 2)
        
        # Проверяем что вторая запись (квадрат) не имеет поля b
        self.assertNotIn('b', data['history'][1])

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

    # Дополнительные endpoints
    def test_health_check(self):
        """Тест проверки работоспособности"""
        r = self.app.get('/health')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('operations_supported', data)
        self.assertIn('history_entries', data)
        self.assertIn('pro_users_count', data)  # Новое поле
        self.assertIn('pro_feature', data)      # Новое поле
        self.assertIn('joke_level', data)       # Новое поле
        self.assertEqual(data['joke_level'], 'maximum')

    def test_get_operations(self):
        """Тест получения списка операций"""
        r = self.app.get('/api/operations')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn('operations', data)
        self.assertGreater(len(data['operations']), 0)
        
        # Проверяем что есть и бинарные и унарные операции
        binary_ops = [op for op in data['operations'] if op['requires_two_numbers']]
        unary_ops = [op for op in data['operations'] if not op['requires_two_numbers']]
        self.assertGreater(len(binary_ops), 0)
        self.assertGreater(len(unary_ops), 0)
        
        # Проверяем наличие поля 'pro'
        for op in data['operations']:
            self.assertIn('pro', op)
            
        # Ищем PRO операцию
        pro_ops = [op for op in data['operations'] if op['pro']]
        self.assertGreater(len(pro_ops), 0)

    def test_activate_pro(self):
        """Тест активации PRO версии"""
        r = self.app.post('/api/activate_pro')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
        self.assertIn('features', data)
        self.assertIn('expires', data)
        self.assertEqual(data['expires'], 'Никогда 😉')
        
        # Проверяем что PRO действительно активирована
        r = self.app.get('/api/calculate?a=1&b=2&operation=add')
        data = r.get_json()
        self.assertTrue(data['pro_activated'])

    def test_get_joke(self):
        """Тест получения шутки"""
        r = self.app.get('/api/joke')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn('joke', data)
        self.assertIn('type', data)
        self.assertIn('laugh_level', data)
        self.assertIsInstance(data['joke'], str)
        self.assertGreater(len(data['joke']), 10)
        self.assertGreaterEqual(data['laugh_level'], 7)
        self.assertLessEqual(data['laugh_level'], 10)

    # Обработка ошибок
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

    def test_missing_parameter_for_binary_operation(self):
        """Тест отсутствия второго параметра для бинарной операции"""
        r = self.app.get('/api/calculate?a=5&operation=add')  # нет b
        self.assertEqual(r.status_code, 200)  # Использует значение по умолчанию 0
        data = r.get_json()
        self.assertEqual(data['result'], 5.0)

    def test_empty_parameters(self):
        """Тест с пустыми параметрами"""
        r = self.app.get('/api/calculate')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn('result', data)
        self.assertEqual(data['result'], 0.0)  # 0 + 0 = 0

    # Тесты для параметров запроса
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

    def test_history_with_unary_operations(self):
        """Тест истории с унарными операциями"""
        self.app.get('/api/calculate?a=4&operation=sqrt')
        self.app.get('/api/calculate?a=5&operation=square')
        self.app.get('/api/calculate?a=2&b=3&operation=add')
        
        r = self.app.get('/api/history')
        data = r.get_json()
        
        self.assertEqual(data['total'], 3)
        
        # Проверяем что унарные операции не имеют поля b в истории
        for item in data['history']:
            if item['operation'] in ['sqrt', 'square']:
                self.assertNotIn('b', item)
            else:
                self.assertIn('b', item)

    # Тесты на граничные случаи
    def test_large_numbers(self):
        """Тест работы с большими числами"""
        r = self.app.get('/api/calculate?a=1e6&b=2e6&operation=add')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 3000000.0)

    def test_decimal_numbers(self):
        """Тест работы с десятичными числами"""
        r = self.app.get('/api/calculate?a=2.5&b=1.5&operation=add')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], 4.0)

    def test_negative_numbers(self):
        """Тест работы с отрицательными числами"""
        r = self.app.get('/api/calculate?a=-5&b=3&operation=add')
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['result'], -2.0)

    def test_operation_order_in_history(self):
        """Тест порядка операций в истории"""
        self.app.get('/api/calculate?a=1&b=2&operation=add')
        self.app.get('/api/calculate?a=3&b=4&operation=multiply')
        
        r = self.app.get('/api/history')
        data = r.get_json()
        
        # Проверяем что операции в правильном порядке
        self.assertEqual(data['history'][0]['operation'], 'add')
        self.assertEqual(data['history'][1]['operation'], 'multiply')

    # Тесты для PRO функциональности
    def test_pro_activation_after_calculation(self):
        """Тест что PRO активируется после первого вычисления"""
        # Первое вычисление - pro_activated должно быть False
        r = self.app.get('/api/calculate?a=1&b=2&operation=add')
        data = r.get_json()
        self.assertFalse(data['pro_activated'])
        
        # Второе вычисление - pro_activated должно быть True
        r = self.app.get('/api/calculate?a=3&b=4&operation=add')
        data = r.get_json()
        self.assertTrue(data['pro_activated'])

    def test_session_persistence(self):
        """Тест сохранения сессии между запросами"""
        # Используем одну сессию для нескольких запросов
        with self.app.session_transaction() as session:
            session['test'] = 'value'
        
        # Проверяем что сессия сохранилась
        with self.app.session_transaction() as session:
            self.assertEqual(session.get('test'), 'value')

    def test_pro_fields_in_response(self):
        """Тест наличия PRO полей в ответах API"""
        r = self.app.get('/api/calculate?a=10&b=5&operation=add')
        data = r.get_json()
        
        # Проверяем все обязательные поля
        required_fields = ['a', 'operation', 'result', 'history_count', 'pro_activated']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Проверяем тип данных
        self.assertIsInstance(data['pro_activated'], bool)
        self.assertIsInstance(data['history_count'], int)

    def test_malformed_json_post(self):
        """Тест обработки некорректного JSON в POST"""
        r = self.app.post('/api/calculate',
                         content_type='application/json',
                         data='{malformed json}')
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertIn('error', data)

    def test_unsupported_method(self):
        """Тест неподдерживаемого метода HTTP"""
        r = self.app.put('/api/calculate')
        self.assertEqual(r.status_code, 405)
        
        r = self.app.delete('/api/calculate')
        self.assertEqual(r.status_code, 405)

    def test_history_with_different_limits(self):
        """Тест истории с разными лимитами"""
        # Добавим записи
        for i in range(20):
            self.app.get(f'/api/calculate?a={i}&b={i}&operation=add')
        
        # Тестируем разные лимиты
        for limit in [1, 5, 10, 20, 50]:
            r = self.app.get(f'/api/history?limit={limit}')
            data = r.get_json()
            expected_len = min(limit, 20)
            self.assertEqual(len(data['history']), expected_len)

    def test_calculation_with_pro_activated(self):
        """Тест вычислений после активации PRO"""
        # Активируем PRO
        self.app.post('/api/activate_pro')
        
        # Выполняем вычисление
        r = self.app.get('/api/calculate?a=7&b=8&operation=add')
        data = r.get_json()
        
        # Проверяем что PRO активирована
        self.assertTrue(data['pro_activated'])
        self.assertEqual(data['result'], 15.0)

if __name__ == '__main__':
    unittest.main()