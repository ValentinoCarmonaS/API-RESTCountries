# sales_system_legacy.py
import os
import json
import csv
from datetime import datetime
from collections import defaultdict

class SalesSystem:
    def __init__(self):
        self.data = []
        self.reports = {}
        self.user_prefs = {
            'currency': 'USD',
            'date_format': '%Y-%m-%d',
            'output_type': 'json'
        }


    def load_data(self, *args):
        for file_path in args:
            try:
                if file_path.endswith('.json'):
                    with open(file_path) as f:
                        new_data = json.load(f)
                        if isinstance(new_data, list):
                            self.data.extend(new_data)
                        else:
                            print(f"Invalid JSON format in {file_path}")
                elif file_path.endswith('.csv'):
                    with open(file_path) as f:
                        reader = csv.DictReader(f)
                        self.data.extend(list(reader))
                else:
                    print(f"Unsupported file format: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")


    def process_user(self, user_id):
        user_sales = [s for s in self.data if str(s.get('user_id')) == str(user_id)]
        
        if not user_sales:
            print(f"No sales found for user {user_id}")
            return False
        
        monthly = defaultdict(lambda: {'total': 0, 'count': 0, 'items': []})
        yearly = defaultdict(lambda: {'total': 0, 'count': 0})

        for sale in user_sales:
            try:
                date = datetime.strptime(sale['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                year_key = date.strftime('%Y')

                price = float(sale['price'])
                quantity = int(sale['quantity'])
                total = price * quantity

                monthly[month_key]['total'] += total
                monthly[month_key]['count'] += 1
                monthly[month_key]['items'].append(sale)

                yearly[year_key]['total'] += total
                yearly[year_key]['count'] += 1
            except (KeyError, ValueError) as e:
                print(f"Invalid sale record: {sale}. Error: {e}")
                continue

        # Calculate averages
        for period in [monthly, yearly]:
            for key in period:
                if period[key]['count'] > 0:
                    period[key]['average'] = period[key]['total'] / period[key]['count']
                else:
                    period[key]['average'] = 0

        self.reports[user_id] = {
            'monthly': dict(monthly),
            'yearly': dict(yearly),
            'user_id': user_id,
            'generated_at': datetime.now().isoformat()
        }
        return True


    def generate_reports(self, output_dir, users=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        users_to_process = users if users else [uid for uid in self.reports.keys()]

        for user_id in users_to_process:
            if user_id not in self.reports:
                if not self.process_user(user_id):  
                    # Creo que esto no es eficiente, ya que debes procesar
                    # al usuario al generar el reporte...
                    # Si ya fue procesado anteriormente (como en el ejemplo),
                    # entonces se procesara 2 veces, 
                    # cuando en realidad ya lo tenes en self.reports[user_id]
                    continue

            report = self.reports[user_id]
            filename = f"sales_report_{user_id}.{self.user_prefs['output_type']}"
            filepath = os.path.join(output_dir, filename)
            try:
                if self.user_prefs['output_type'] == 'json':
                    with open(filepath, 'w') as f:
                        json.dump(report, f, indent=2)
                elif self.user_prefs['output_type'] == 'csv':
                    self._generate_csv_report(report, filepath)
                else:
                    print(f"Unsupported output format: {self.user_prefs['output_type']}")
                    continue

                print(f"Generated report: {filepath}")
            except IOError as e:
                print(f"Failed to write report for user {user_id}: {e}")


    def _generate_csv_report(self, report, filepath):
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Period', 'Total Sales', 'Average Sale', 'Number of Sales'])

            for period in ['monthly', 'yearly']:
                for period_name, data in report[period].items():
                    writer.writerow([
                    period_name,
                    data['total'],
                    data.get('average', 0),
                    data['count']
                    ])


    def set_preferences(self, **prefs):
        for key, value in prefs.items():
            if key in self.user_prefs:
                self.user_prefs[key] = value
            else:
                print(f"Ignoring unknown preference: {key}")

# Example usage:
if __name__ == "__main__":
    system = SalesSystem()
    system.load_data('./sales.json', './sales.csv')
    system.set_preferences(output_type='csv', currency='EUR')
    system.process_user(42)
    system.process_user(101)
    system.generate_reports('reports', users=[42, 101])