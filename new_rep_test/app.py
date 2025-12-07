from flask import Flask, request, jsonify, render_template
import math
from typing import List, Dict, Union, Optional

app = Flask(__name__)

# Хранилище истории вычислений (в памяти)
calculation_history: List[Dict[str, Union[str, float, None]]] = []

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

@app.route('/')
def home():
    """Главная страница с веб-интерфейсом калькулятора"""
    return render_template('index.html', history=calculation_history[-10:])

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
        
        # Формируем запись для истории
        history_entry = {
            'a': a,
            'operation': operation,
            'display_operation': get_operation_display_name(operation),
            'result': result,
            'timestamp': math.floor(request.environ.get('REQUEST_TIME', 0))
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
            'history_count': len(calculation_history)
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
        {'value': 'add', 'name': 'Сложение', 'symbol': '+', 'requires_two_numbers': True},
        {'value': 'subtract', 'name': 'Вычитание', 'symbol': '-', 'requires_two_numbers': True},
        {'value': 'multiply', 'name': 'Умножение', 'symbol': '×', 'requires_two_numbers': True},
        {'value': 'divide', 'name': 'Деление', 'symbol': '÷', 'requires_two_numbers': True},
        {'value': 'power', 'name': 'Степень', 'symbol': '^', 'requires_two_numbers': True},
        {'value': 'root', 'name': 'Корень n-ной степени', 'symbol': 'ⁿ√', 'requires_two_numbers': True},
        {'value': 'sqrt', 'name': 'Квадратный корень', 'symbol': '√', 'requires_two_numbers': False},
        {'value': 'square', 'name': 'Квадрат числа', 'symbol': '²', 'requires_two_numbers': False},
        {'value': 'cube', 'name': 'Куб числа', 'symbol': '³', 'requires_two_numbers': False},
    ]
    return jsonify({'operations': operations})

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности приложения"""
    return jsonify({
        'status': 'healthy', 
        'service': 'calculator-api',
        'version': '1.1',
        'operations_supported': 9,
        'history_entries': len(calculation_history)
    })

def main():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    main()