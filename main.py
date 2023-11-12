import json
import re
import os
import datetime
import pyinputplus as pyip

files = [file for file in os.listdir('./scores')]
content = [open('./scores/' + file, 'r').read() for file in files]


def get_content():
    content = []

    for f in files:
        file_data = open('./scores/' + f, 'r').readlines()
        d = {}
        d['data'] = file_data
        d['name'] = f.replace('acft_raw_', '').replace(
            '.txt', '').replace('_', ' ')

        content.append(d)

    return content


def create_exercises():
    exercises = {"male": {}, "female": {}}
    for i, block in enumerate(get_content()):

        male = get_ages(block['data'])[0]
        female = get_ages(block['data'])[1]

        exercises['male'][block['name']] = male
        exercises['female'][block['name']] = female

    return exercises


def get_points(data, col):
    points = {}
    for i, line in enumerate(data):
        l = line.split()
        points[l[0]] = l[col]

    return points


def get_ages(data):
    headers = ["1721M", "1721F", "2226M", "2226F", "2731M", "2731F", "3236M", "3236F", "3741M",
               "3741F", "4246M", "4246F", "4751M", "4751F", "5256M", "5256F", "5761M", "5761F", "62M", "62F"]
    m_h = [h for h in headers if re.search('M', h)]
    f_h = [h for h in headers if re.search('F', h)]
    m_result = {}
    f_result = {}
    m = 1
    f = 2
    for i, h in enumerate(m_h):
        min = h[:2]
        max = h[2:4]
        age = f"{min}-{max}" if int(min) != 62 else f"{min}"
        m_result[age] = get_points(data, m)
        m += 2

    for i, h in enumerate(f_h):
        min = h[:2]
        max = h[2:4]
        age = f"{min}-{max}" if int(min) != 62 else f"{min}"
        f_result[age] = get_points(data, f)
        f += 2

    return m_result, f_result


d = create_exercises()
with open("data.json", 'w') as f:
    json.dump(d, f)


def get_points(user_score, scores, plank=False):
    points = None
    max_score = scores["100"]
    min_score = scores["0"]

    if isinstance(user_score, int):
        max_score = int(max_score)
        min_score = int(min_score)

        if user_score <= min_score:
            points = 0
        elif user_score >= max_score:
            points = 100
        else:
            for k in scores:
                if scores[k] == '---' or scores[k] == '--':
                    continue
                elif user_score >= int(scores[k]):
                    points = k
                    break
    elif isinstance(user_score, datetime.datetime):

        if plank:
            points = get_plank_score(user_score, scores)
            return points

        max_time = datetime.datetime.strptime(scores["100"], "%M:%S")
        min_time = datetime.datetime.strptime(scores["0"], "%M:%S")

        if user_score <= max_time:
            points = 100
        elif user_score >= min_time:
            points = 0
        else:
            for k in scores:
                if scores[k] != '---' and user_score >= datetime.datetime.strptime(scores[k], '%M:%S'):
                    points = k
    elif isinstance(user_score, float):
        max_distance = float(scores["100"])
        min_distance = float(scores["0"])

        if user_score >= max_distance:
            points = 100
        elif user_score <= min_distance:
            points = 0
        else:
            for k in scores:
                if scores[k] != '---' and user_score >= float(scores[k]):
                    points = k
                    break

    return points


def get_plank_score(user_score, scores):
    points = None
    max_time = datetime.datetime.strptime(scores["100"], "%M:%S")
    min_time = datetime.datetime.strptime(scores["0"], "%M:%S")

    if user_score >= max_time:
        points = 100
    elif user_score <= min_time:
        points = 0
    else:
        for k in scores:
            if scores[k] != '---' and user_score >= datetime.datetime.strptime(scores[k], "%M:%S"):
                points = k
                break

    return points


def get_user_info():
    user = {
        "details": {
            "name": None,
            "age": None,
            "gender": None,
        },
        "passed": False,
        "scores": {e: None for e in events},
        "final_score": 0
    }

    detail_formats = {
        "name": pyip.inputStr("Enter Name: "),
        "age": pyip.inputInt("Enter Age: ", min=17, lessThan=100),
        "gender": pyip.inputMenu(['male', 'female'], numbered=True),
    }

    score_formats = {
        "deadlift": pyip.inputInt('Deadlift: ', greaterThan=0),
        "run": pyip.inputDatetime("2 Mile: ", formats=["%M:%S"]),
        "plank": pyip.inputDatetime("Plank: ", formats=["%M:%S"]),
        "power throw": pyip.inputFloat("Power Throw:"),
        "pushup": pyip.inputNum('Pushups: ', greaterThan=0),
        "sprint drag carry": pyip.inputDatetime("Sprint Drag Carry: ", formats=["%M:%S"]),
    }

    user["details"] = detail_formats
    user["scores"] = score_formats

    return user


events = ["deadlift", "run", "plank",
          "power throw", "pushup", 'sprint drag carry']

json_data = open('./data.json')
data = json.load(json_data)

user = get_user_info()

for i, e in enumerate(events):
    g = user["details"]["gender"]
    age_range = [k for k, v in data[user['details']['gender']][e].items()
                 if int(k.split('-')[0]) <= user['details']['age'] <= int(k.split('-')[1])]
    scores = data[g][e][age_range[0]]
    user_score = user["scores"][e]
    plank = True if e == "plank" else False

    points = int(get_points(user_score, scores, plank))

    if points >= 60:
        user["final_score"] += points
    elif points < 60:
        print(f"Failed with {user['final_score']} points")
        break

    if i == len(events) - 1 and user['final_score'] >= 360:
        user['passed'] = True


if user['passed']:
    print(f"{user['details']['name']} passed with {user['final_score']} points")
