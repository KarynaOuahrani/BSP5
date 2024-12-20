from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)


data = pd.read_csv('DataExtract.csv')  

data = data[
    (data['Country Or Territory'].isin(['Luxembourg', 'Germany', 'France', 'Italy', 'Netherlands', 'Poland', 'Spain'])) &
    (data['Year'] >= 2014) & 
    (data['Year'] <= 2021) & 
    (data['Air Pollutant'].isin(['NO2', 'O3', 'PM2.5'])) 
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_pollution_data', methods=['GET'])
def get_pollution_data():
    year = int(request.args.get('year'))
    pollutant = request.args.get('pollutant')
    country = request.args.get('country') 
    filtered_data = data[(data['Year'] == year) & 
                         (data['Air Pollutant'] == pollutant) & 
                         (data['Country Or Territory'] == country)]
    
    if not filtered_data.empty:
        average_value = filtered_data['Air Pollution Average [ug/m3]'].mean()
        response = {'average_value': round(average_value, 2)}
    else:
        response = {'average_value': None}

    return jsonify(response)

@app.route('/get_pollution_trends', methods=['GET'])
def get_pollution_trends():
    country = request.args.get('country')
    pollutant = request.args.get('pollutant')

    if not country or not pollutant:
        return jsonify({'error': 'Invalid or missing parameters'}), 400

    filtered_data = data[(data['Country Or Territory'] == country) & 
                         (data['Air Pollutant'] == pollutant)]

    if not filtered_data.empty:
        filtered_data = (
            filtered_data.groupby('Year')['Air Pollution Average [ug/m3]']
            .mean()
            .reset_index()
            .sort_values('Year')  
        )
        years = filtered_data['Year'].astype(int).tolist()
        values = filtered_data['Air Pollution Average [ug/m3]'].astype(float).tolist()

        response = {
            'years': years,
            'values': [round(v, 2) for v in values]
        }
    else:
        response = {'years': [], 'values': []}

    return jsonify(response)

@app.route('/get_country_comparison', methods=['GET'])
def get_country_comparison():
    year = int(request.args.get('year'))
    pollutant = request.args.get('pollutant')

    filtered_data = data[(data['Year'] == year) & 
                         (data['Air Pollutant'] == pollutant)]

    if not filtered_data.empty:
        countries = filtered_data['Country Or Territory'].unique().tolist()
        values = [
            float(filtered_data[filtered_data['Country Or Territory'] == country]['Air Pollution Average [ug/m3]'].mean())
            for country in countries
        ]
        response = {'countries': countries, 'values': [round(v, 2) for v in values]}
    else:
        response = {'countries': [], 'values': []}

    return jsonify(response)

@app.route('/get_all_countries_data', methods=['GET'])
def get_all_countries_data():
    year = int(request.args.get('year'))
    pollutant = request.args.get('pollutant')

    filtered_data = data[(data['Year'] == year) & 
                         (data['Air Pollutant'] == pollutant)]

    if not filtered_data.empty:
        countries = filtered_data['Country Or Territory'].unique().tolist()
        data_by_country = {
            country: round(
                float(filtered_data[filtered_data['Country Or Territory'] == country]['Air Pollution Average [ug/m3]'].mean()),
                2
            )
            for country in countries
        }
        return jsonify(data_by_country)
    return jsonify({})



if __name__ == '__main__':
    app.run(debug=True)

