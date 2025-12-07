from flask import Flask, request, jsonify, render_template, session
import math
import random
import secrets
from typing import List, Dict, Union, Optional
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Для работы сессий

# Хранилище истории вычислений (в памяти)
calculation_history: List[Dict[str, Union[str, float, None]]] = []

# Флаг первого вычисления для каждого пользователя (в сессии)
def is_first_calculation():
    """Проверяет, было ли первое вычисление у пользователя"""
    return session.get('first_calculation', True)

def mark_calculation_done():
    """Отмечает что первое вычисление выполнено"""
    session['first_calculation'] = False

def calculate(a: float, b: Optional[float], operation: str) -> float:
    """
    Выполняет математическую операцию
    Для унарных операций (sqrt, square, cube) параметр b игнорируется
    """
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else float('inf'),
        'power': lambda x, y: x ** y,
        'root': lambda x, y: x ** (1/y) if y != 0 and x >= 0 else float('nan'),
        'sqrt': lambda x, y: math.sqrt(x) if x >= 0 else float('nan'),
        'square': lambda x, y: x ** 2,
        'cube': lambda x, y: x ** 3,
    }
    
    if operation not in operations:
        raise ValueError(f"Неподдерживаемая операция: {operation}")
    
    # Для унарных операций используем только a
    if operation in ['sqrt', 'square', 'cube']:
        return operations[operation](a, 0)  # b игнорируется
    
    # Для бинарных операций проверяем b
    if b is None:
        raise ValueError(f"Для операции '{operation}' требуется второй параметр")
    
    return operations[operation](a, b)

def get_operation_display_name(operation: str) -> str:
    """Возвращает символ операции для отображения"""
    display_names = {
        'add': '+',
        'subtract': '-',
        'multiply': '×',
        'divide': '÷',
        'power': '^',
        'root': '√',
        'sqrt': '√',
        'square': '²',
        'cube': '³'
    }
    return display_names.get(operation, operation)

def generate_pro_modal_data():
    """Генерирует случайные данные для PRO модалки"""
    # Случайные цены с разной вероятностью
    prices = [
        ('$0.00', 30),  # 30% вероятность
        ('$0.01', 20),  # 20% вероятность
        ('$1.99', 15),  # 15% вероятность
        ('$4.99', 10),  # 10% вероятность
        ('$9.99', 8),   # 8% вероятность
        ('$19.99', 6),  # 6% вероятность
        ('$99.99', 5),  # 5% вероятность
        ('$999.99', 4), # 4% вероятность
        ('БЕСПЛАТНО', 2), # 2% вероятность
    ]
    
    # Выбираем цену по весам
    total_weight = sum(weight for _, weight in prices)
    r = random.uniform(0, total_weight)
    upto = 0
    for price, weight in prices:
        if upto + weight >= r:
            pro_price = price
            break
        upto += weight
    
    # Фейковые отзывы
    fake_reviews = [
        {"name": "Алексей П.", "text": "Лучший калькулятор! PRO версия изменила мою жизнь!", "rating": "★★★★★", "time": "2 часа назад"},
        {"name": "Мария С.", "text": "Теперь считаю быстрее коллег на работе! Кнопка 'Равно' просто магия!", "rating": "★★★★★", "time": "Вчера"},
        {"name": "Дмитрий К.", "text": "Долго сомневался, но не жалею! PRO версия стоит каждого цента (хотя она бесплатная).", "rating": "★★★★☆", "time": "3 дня назад"},
        {"name": "Ольга В.", "text": "Перешла с обычного калькулятора. Не жалею! Интерфейс стал красивее.", "rating": "★★★★★", "time": "Неделю назад"},
        {"name": "Иван Г.", "text": "Мои дети теперь делают домашку в 2 раза быстрее! Спасибо за PRO!", "rating": "★★★★★", "time": "2 недели назад"},
        {"name": "Сергей М.", "text": "Наконец-то могу использовать кнопку 'Равно'! Раньше приходилось угадывать результат.", "rating": "★★★★★", "time": "Месяц назад"},
        {"name": "Анна Л.", "text": "Купила PRO версию за $999.99 и не жалею! Шутка, она бесплатная 😂", "rating": "★★★★★", "time": "Только что"},
        {"name": "Павел Р.", "text": "После активации PRO у меня выросла зарплата! Совпадение? Не думаю!", "rating": "★★★★★", "time": "5 минут назад"},
    ]
    
    # Выбираем 3 случайных отзыва
    selected_reviews = random.sample(fake_reviews, 3)
    
    # Случайное количество "уже купивших"
    already_sold = random.randint(1542, 9876)
    
    # Случайный процент "довольных пользователей"
    satisfaction_rate = random.randint(96, 100)
    
    return {
        'pro_price': pro_price,
        'fake_reviews': selected_reviews,
        'already_sold': already_sold,
        'satisfaction_rate': satisfaction_rate,
        'current_time': datetime.now().strftime("%H:%M"),
        'fake_timer': random.randint(5, 15),  # Случайное время для таймера
    }

@app.route('/')
def home():
    """Главная страница с веб-интерфейсом калькулятора"""
    show_pro_modal = is_first_calculation()
    
    modal_data = {}
    if show_pro_modal:
        modal_data = generate_pro_modal_data()
    
    return render_template('index.html', 
                         history=calculation_history[-10:],
                         show_pro_modal=show_pro_modal,
                         **modal_data)

@app.route('/api/calculate', methods=['GET', 'POST'])
def api_calculate():
    """
    API endpoint для калькулятора
    
    GET параметры: 
      - a: число (обязательно)
      - b: число (необязательно для унарных операций)
      - operation: add|subtract|multiply|divide|power|root|sqrt|square|cube
    """
    try:
        if request.method == 'GET':
            # Обработка GET запроса
            a = float(request.args.get('a', 0))
            operation = request.args.get('operation', 'add')
            
            # Определяем, нужно ли значение b
            if operation in ['sqrt', 'square', 'cube']:
                b = None
                b_value = None
            else:
                b_str = request.args.get('b', '0')
                b = float(b_str) if b_str != '' else 0
                b_value = b
                
        elif request.method == 'POST':
            # Обработка POST запроса
            if not request.is_json:
                return jsonify({'error': 'Content-Type должен быть application/json'}), 400
            
            data = request.get_json()
            a = float(data.get('a', 0))
            operation = data.get('operation', 'add')
            
            if operation in ['sqrt', 'square', 'cube']:
                b = None
                b_value = None
            else:
                b = float(data.get('b', 0))
                b_value = b
        else:
            return jsonify({'error': 'Метод не поддерживается'}), 405
        
        # Выполнение вычисления
        result = calculate(a, b, operation)
        
        # Помечаем что первое вычисление выполнено
        if is_first_calculation():
            mark_calculation_done()
        
        # Формируем запись для истории
        history_entry = {
            'a': a,
            'operation': operation,
            'display_operation': get_operation_display_name(operation),
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Добавляем b только если операция не унарная
        if operation not in ['sqrt', 'square', 'cube']:
            history_entry['b'] = b_value
        
        calculation_history.append(history_entry)
        
        # Формируем ответ
        response_data = {
            'a': a,
            'operation': operation,
            'display_operation': get_operation_display_name(operation),
            'result': result,
            'history_count': len(calculation_history),
            'pro_activated': not is_first_calculation(),  # True если PRO активирована
        }
        
        if operation not in ['sqrt', 'square', 'cube']:
            response_data['b'] = b_value
        
        return jsonify(response_data)
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Неверные параметры: {str(e)}'}), 400
    except ZeroDivisionError:
        return jsonify({'error': 'Деление на ноль'}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Получить историю вычислений"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'history': calculation_history[-limit:],
        'total': len(calculation_history)
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Очистить историю вычислений"""
    calculation_history.clear()
    return jsonify({'message': 'История очищена', 'total': 0})

@app.route('/api/operations', methods=['GET'])
def get_operations():
    """Получить список поддерживаемых операций"""
    operations = [
        {'value': 'add', 'name': 'Сложение', 'symbol': '+', 'requires_two_numbers': True, 'pro': False},
        {'value': 'subtract', 'name': 'Вычитание', 'symbol': '-', 'requires_two_numbers': True, 'pro': False},
        {'value': 'multiply', 'name': 'Умножение', 'symbol': '×', 'requires_two_numbers': True, 'pro': False},
        {'value': 'divide', 'name': 'Деление', 'symbol': '÷', 'requires_two_numbers': True, 'pro': False},
        {'value': 'power', 'name': 'Степень', 'symbol': '^', 'requires_two_numbers': True, 'pro': True},
        {'value': 'root', 'name': 'Корень n-ной степени', 'symbol': 'ⁿ√', 'requires_two_numbers': True, 'pro': True},
        {'value': 'sqrt', 'name': 'Квадратный корень', 'symbol': '√', 'requires_two_numbers': False, 'pro': True},
        {'value': 'square', 'name': 'Квадрат числа', 'symbol': '²', 'requires_two_numbers': False, 'pro': True},
        {'value': 'cube', 'name': 'Куб числа', 'symbol': '³', 'requires_two_numbers': False, 'pro': True},
        {'value': 'pro_magic', 'name': 'PRO Магия ✨', 'symbol': '🔮', 'requires_two_numbers': False, 'pro': True},
    ]
    return jsonify({'operations': operations})

@app.route('/api/activate_pro', methods=['POST'])
def activate_pro():
    """Активирует PRO версию для пользователя"""
    mark_calculation_done()
    return jsonify({
        'status': 'success',
        'message': 'PRO версия активирована!',
        'features': [
            'Кнопка "Равно" разблокирована',
            'Все цифры 0-9 доступны',
            'Расширенные операции активированы',
            'Реклама отключена'
        ],
        'expires': 'Никогда 😉'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности приложения"""
    pro_users = len([s for s in [session] if not s.get('first_calculation', True)])
    
    return jsonify({
        'status': 'healthy', 
        'service': 'calculator-api',
        'version': '2.0',
        'operations_supported': 10,
        'history_entries': len(calculation_history),
        'pro_users_count': pro_users,
        'pro_feature': True,
        'joke_level': 'maximum'
    })

@app.route('/api/joke', methods=['GET'])
def get_joke():
    """Возвращает случайную шутку про калькуляторы (для PRO модалки)"""
    jokes = [
        "Почему калькулятор пошел к психологу? У него были комплексы!",
        "Что сказал калькулятор своей жене? 'Дорогая, ты просто невыносима!'",
        "Почему калькулятор плохой танцор? Он всегда считает шаги!",
        "Как калькулятор признается в любви? 'Ты плюс моя жизнь равно счастье!'",
        "Почему калькулятор не играет в прятки? Потому что его всегда находят по точкам!",
        "Что калькулятор сказал на свидании? 'Давай сложим наши сердца!'",
    ]
    return jsonify({
        'joke': random.choice(jokes),
        'type': 'calculator_humor',
        'laugh_level': random.randint(7, 10)
    })

def main():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    main()