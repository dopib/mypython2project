from flask import Flask, render_template, request, redirect, url_for
import requests


app = Flask(__name__)



Api ="HvsF3SunhYTQ2zRini7YSULFhhfOh3HC"


def get_loc_key(city):
    try:
        search_url = (
            f"http://dataservice.accuweather.com/locations/v1/cities/search"
            f"?apikey={Api}&q={city}&language=ru-ru"
        )
        response = requests.get(search_url)
        response.raise_for_status()
        locations = response.json()
        if locations:
            return locations[0]['Key']
    except requests.RequestException as e:
        print(f"Ошибка : {e}")
    return None


def get_weath(loc_key):
    try:
        weather_url = (
            f"http://dataservice.accuweather.com/currentconditions/v1/{loc_key}"
            f"?apikey={Api}&language=ru-ru&details=true"
        )
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_info = response.json()
        if weather_info:
            weather = weather_info[0]
            return {
                "temperature": weather['Temperature']['Metric']['Value'],
                "humidity": weather['RelativeHumidity'],
                "wind_speed": weather['Wind']['Speed']['Metric']['Value'],
                "precipitation": weather['HasPrecipitation'],
                "description": weather['WeatherText']
            }
    except requests.RequestException as e:
        print(f"Ошибка: {e}")
    return None


def show_data(city):
    key = get_loc_key(city)
    if key:
        weather = get_weath(key)
        if weather:
            return {
                "city": city,
                "temperature": weather["temperature"],
                "humidity": weather["humidity"],
                "wind_speed": weather["wind_speed"],
                "precipitation": weather["precipitation"],
                "description": weather["description"]
            }
    return None


def mark_weath(weather_data):
    unfavorable = []
    temp = weather_data['temperature']
    humidity = weather_data['humidity']
    if temp < -15 or temp > 25:
        unfavorable.append('температура')
    if humidity > 75:
        unfavorable.append('влажность')

    return unfavorable if unfavorable else None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form.get('start_city')
    end_city = request.form.get('end_city')


    start_weather = show_data(start_city)
    end_weather = show_data(end_city)

    if not start_weather or not end_weather:
        return redirect(url_for('home'))

    start_unfavorable = mark_weath(start_weather)
    end_unfavorable = mark_weath(end_weather)

    return render_template(
        'result.html',
        start_weather=start_weather,
        end_weather=end_weather,
        start_unfavorable=start_unfavorable,
        end_unfavorable=end_unfavorable
    )

if __name__ == '__main__':
    app.run(debug=True)
