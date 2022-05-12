from flask import render_template, request, jsonify
from requests.exceptions import ConnectionError, ReadTimeout

from model import *
import datetime
import requests

esp_url = "http://11.1.30.29:80"


def read_data_from_esp():
    try:
        url = f'{esp_url}/sensor_data'
        res = requests.get(url, timeout=0.05)
        content = res.text.split("/")

        data = Data(datetime=datetime.datetime.now(), water_temp_c=float(content[0]), air_temp_c=float(content[1]),
                    humidity=float(content[2]), water_level=int(content[3]), led_state=int(content[4]),
                    pump_state=int(content[5]))
        db.session.add(data)
        db.session.commit()
    except:
        print("Error esp")
        return False


@app.route('/api/data', methods=['GET'])
def api_data():
    data = get_last_data()
    dict_json = {'datetime': data.datetime}
    sensors = [{'id': "tempWaterC", 'name': "Температура воды", 'value': data.water_temp_c, 'measure': '°'},
               {'id': "tempAirC", 'name': "Температура воздуха", 'value': data.air_temp_c, 'measure': '°'},
               {'id': "humidity", 'name': "Влажность", 'value': data.humidity, 'measure': '%'}]
    control = [{'id': "pumpState", 'name': "Полив", 'toggleRoute': "/pump/config", 'state': data.pump_state},
               {'id': "ledState", 'name': "Свет", 'toggleRoute': "/led/config", 'state': data.led_state}]
    dict_json.update({'sensors': sensors})
    dict_json.update({'control': control})
    response = jsonify(dict_json)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def get_last_data(attempt=0):
    data = db.session.query(Data).all()

    data = data[len(data) - 1]

    return data


def water_info():
    data = get_last_data()
    dict_json = {}
    if data is not None:
        if 18 < data.water_temp_c < 23:
            dict_json.update({"normal": True})
        else:
            dict_json.update({"normal": False})
            dict_json.update({
                "message": f"Температура воды вышла за пределы нормы"
                           f",пожалуйста перенесите теплицу в другуое место!"})
    return dict_json


@app.route('/led/config', methods=['GET'])
def led_config():
    read_data_from_esp()
    data = get_last_data()
    if data is not None:
        if data.led_state == 1:
            data.led_state = 0
            db.session.add(data)
            db.session.commit()
        else:
            data.led_state = 1
            db.session.add(data)
            db.session.commit()
        read_data_from_esp()
        esp_get("led", data.led_state)
    return show_main()


@app.route('/pump/config', methods=['GET'])
def pump_config():
    read_data_from_esp()
    data = get_last_data()
    if data is not None:
        if data.pump_state == 1:
            data.pump_state = 0
            db.session.add(data)
            db.session.commit()
        else:
            data.pump_state = 1
            db.session.add(data)
            db.session.commit()
        if esp_get("pump", data.pump_state):
            db.session.add(data)
            db.session.commit()
        read_data_from_esp()
    return show_main()


def esp_get(api, part):
    try:
        url = f'{esp_url}/{api}/{part}'
        requests.get(url)
        return True
    except ConnectionError:
        print("Error esp")
    return False


def check_led():
    if datetime.datetime.now().hour == 22:
        url = 'https://esp?led=0'
        res = requests.get(url)


def air_info():
    data = get_last_data()
    dict_json = {}
    if data is not None:
        if 20 < data.air_temp_c < 25:
            dict_json.update({"normal": True})
        else:
            dict_json.update({"normal": False})
            dict_json.update({
                "message": f"Температура воздуха вышла за пределы нормы,"
                           f" пожалуста перенесите теплицу в другуое место"})
    return dict_json


# def humidity():
#     data = db.session.query(Data).all()
#     humidity_now = data[len(data) - 1]
#     dict_json = {}
#     dict_json.update({"value": humidity_now.humidity})
#     if 18 < humidity_now.humidity < 25:
#         dict_json.update({"normal": True})
#         dict_json.update({"message": f"Показатель в норме: {humidity_now.humidity}"})
#     else:
#         dict_json.update({"normal": False})
#         dict_json.update({
#             "message": f"Влажность ниже нормы: {humidity_now.humidity}"})
#     return dict_json


# def water_level():
#     data = db.session.query(Data).all()
#     level = data[len(data) - 1]
#     dict_json = {}
#     dict_json.update({"value": level.water_level})
#     if level.water_level == 1:
#         dict_json.update({"normal": True})
#         dict_json.update({"message": f"Уровень воды в порядке: {level.water_level}"})
#     else:
#         dict_json.update({"normal": False})
#         dict_json.update({
#             "message": f": Пожалуста пополните бак"})
#     return dict_json


def led_info():
    data = get_last_data()
    dict_json = {}

    if data is not None:
        if data.led_state == 1:
            dict_json.update({"normal": True})
            dict_json.update({"message": "Освещение включено"})
        else:
            dict_json.update({"normal": False})
            dict_json.update({
                "message": "Освещение выключено"})
    return dict_json


def pump_info():
    data = get_last_data()
    dict_json = {}
    if data is not None:
        if data.pump_state == 1:
            dict_json.update({"normal": True})
            dict_json.update({"message": "Насос включено"})
        else:
            dict_json.update({"normal": False})
            dict_json.update({
                "message": "Насос выключено"})
    return dict_json


@app.route('/login')
def show_login():
    return render_template("login.html")


@app.route('/information')
def show_info():
    return render_template("information.html")


@app.route('/')
def show_main():
    data = get_last_data()
    print(type(data.id))
    return render_template("main.html", water_info=water_info(), air_info=air_info(), led_info=led_info(),
                           pump_info=pump_info(), data=get_last_data())


if __name__ == '__main__':
    db.create_all()
    app.run()
