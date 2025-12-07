from flask import Flask, request, jsonify, render_template
import math
from typing import List, Dict, Union

app = Flask(__name__)

# Хранилище истории вычислений (в памяти)
calculation_history: List[Dict[str, Union[str, float]]] = []

def calculate(a: float, b: float, operation: str) -> float:
    """
    Выполняет математическую операцию
    """
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else float('inf'),
        'power': lambda x, y: x ** y,
        'root': lambda x, y: x ** (1/y) if y != 0 and x >= 0 else float('nan')
    }
    
    if operation not in operations:
        raise ValueError(f"Неподдерживаемая операция: {operation}")
    
    return operations[operation](a, b)

@app.route('/')
def home():
    """Главная страница с веб-интерфейсом калькулятора"""
    return render_template('index.html', history=calculation_history[-10:])  # последние 10 операций

@app.route('/api/calculate', methods=['GET', 'POST'])
def api_calculate():
    """
    API endpoint для калькулятора
    
    GET параметры: a, b, operation
    POST JSON: {"a": число, "b": число, "operation": "add|subtract|multiply|divide|power|root"}
    """
    if request.method == 'GET':
        # Обработка GET запроса
        try:
            a = float(request.args.get('a', 0))
            b = float(request.args.get('b', 0))
            operation = request.args.get('operation', 'add')
        except (TypeError, ValueError):
            return jsonify({'error': 'Неверные параметры'}), 400
    
    elif request.method == 'POST':
        # Обработка POST запроса
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400
        
        data = request.get_json()
        try:
            a = float(data.get('a', 0))
            b = float(data.get('b', 0))
            operation = data.get('operation', 'add')
        except (TypeError, ValueError):
            return jsonify({'error': 'Неверный формат данных'}), 400
    
    # Выполнение вычисления
    try:
        result = calculate(a, b, operation)
        
        # Сохраняем в историю
        calculation_history.append({
            'a': a,
            'b': b,
            'operation': operation,
            'result': result
        })
        
        return jsonify({
            'a': a,
            'b': b,
            'operation': operation,
            'result': result,
            'history_count': len(calculation_history)
        })
    
    except ZeroDivisionError:
        return jsonify({'error': 'Деление на ноль'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

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

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности приложения"""
    return jsonify({'status': 'healthy', 'service': 'calculator-api'})

def main():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    main()