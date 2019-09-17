import hmac
import base64
import datetime

from pytz import timezone
from . import consts as c


def sign(message, secretKey):
    mac = hmac.new(bytes(secretKey, encoding="utf8"), bytes(message, encoding="utf-8"), digestmod="sha256")
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase):
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase

    return header


def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'
    return url[0:-1]


def get_timestamp():
    now = datetime.datetime.utcnow()
    t = now.isoformat()[:-3]
    return t + "Z"


def get_instrument_id(symbol, contract_type):
    symbol = symbol.upper().replace("_", "-")
    due_date = get_the_due(contract_type)
    return "{}-{}".format(symbol, due_date.strftime("%y%m%d"))


def get_the_due(contract_type, timestamp=None):
    now = datetime.datetime.now(tz=timezone("Asia/Shanghai"))
    if timestamp is not None:
        now = datetime.datetime.fromtimestamp(timestamp / 1000, tz=timezone("Asia/Shanghai"))
    last_friday = datetime.datetime(now.year, now.month, now.day, 16, 0, 0, 0, timezone("Asia/Shanghai"))
    weekday = now.weekday()

    if weekday > 4 or (weekday == 4 and now.hour >= 16):
        last_friday += datetime.timedelta(days=4 - weekday)
    else:
        last_friday += datetime.timedelta(days=-3 - weekday)

    this_week = last_friday + datetime.timedelta(days=7)
    next_week = last_friday + datetime.timedelta(days=14)
    if contract_type == "this_week":
        return this_week
    elif contract_type == "next_week":
        return next_week
    start_quarter = get_the_quarter(now)
    the_quarter = start_quarter + datetime.timedelta(days=-1)
    while the_quarter.weekday() != 4:
        the_quarter += datetime.timedelta(days=-1)

    the_quarter = datetime.datetime(
        the_quarter.year,
        the_quarter.month,
        the_quarter.day,
        16, 0, 0, 0, tzinfo=timezone("Asia/Shanghai"),
    )

    if now + datetime.timedelta(weeks=2) < the_quarter:
        return the_quarter
    return the_quarter + datetime.timedelta(days=91)


def get_the_contract_type(due_timestamp, timestamp = None):
    minus = due_timestamp - timestamp

    if minus< 7*24*60*60*1000:
        return "this_week"
    elif minus<14*24*60*60*1000:
        return "next_week"
    else:
        return "quarter"


def get_the_quarter(date):
    num = 0
    flags = [4, 7, 10, 13]
    the_month = date.month
    for i in range(len(flags)):
        if the_month < flags[i]:
            num = i
            break
    return datetime.datetime(
        date.year + int(flags[num] / 12),
        flags[num] % 12,
        1, 0, 0, 0, 0, tzinfo=timezone("Asia/Shanghai"),
    )


def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == "{}" or str(body) == "None":
        body = ""
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    mac = hmac.new(bytes(secret_key, encoding="utf8"), bytes(message, encoding="utf-8"), digestmod="sha256")
    d = mac.digest()
    return base64.b64encode(d)
