from email.policy import default
from tabnanny import check
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.staticfiles import StaticFiles
from app.configs import Config
from app.utilities.session import Session
from app.models.auth import AuthModel
from app.models.articles import ArticleModel
from app.models.reservation import ReservationModel
from app.utilities.check_login import check_login
import datetime
import json

app = FastAPI()
app.mount("/app/statics", StaticFiles(directory="app/statics"), name="static")
templates = Jinja2Templates(directory="/app/templates")
config = Config()
session = Session(config)


@app.get("/")
def index(request: Request):
    """
    トップページを返す
    :param request: Request object
    :return:
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def register(request: Request):
    """
    新規登録ページ
    :param request:
    :return:
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/office/register")
def office_register(request: Request):
    return templates.TemplateResponse("office_register.html", {"request": request})


# 一般ユーザのログイン処理
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    ログイン処理
    :param request:
    :param username:
    :param password:
    :return:
    """
    auth_model = AuthModel(config)
    [result, user] = auth_model.login(username, password)
    if not result:
        # ユーザが存在しなければトップページへ戻す
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"}
        )
    response = RedirectResponse("/menue", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


# 企業側ユーザのログイン処理
@app.post("/office/login")
def office_login(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    auth_model = AuthModel(config)
    [result, user] = auth_model.office_login(username, password)
    if not result:
        # ユーザが存在しなければトップページへ戻す
        return templates.TemplateResponse(
            "office_index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"}
        )
    response = RedirectResponse("/office/menue", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


# 企業側のメニュー画面表示
@app.get("/office/menue")
@check_login
def display_office_menue(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "office_menue.html", {"request": request, "user": user, "id": session_id}
    )


@app.post("/register")
def create_user(username: str = Form(...), password: str = Form(...)):
    """
    ユーザ登録をおこなう
    フォームから入力を受け取る時は，`username=Form(...)`のように書くことで受け取れる
    :param username: 登録するユーザ名
    :param password: 登録するパスワード
    :return: 登録が完了したら/blogへリダイレクト
    """
    auth_model = AuthModel(config)
    auth_model.create_user(username, password)
    user = auth_model.find_user_by_name_and_password(username, password)
    response = RedirectResponse(url="/menue", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.post("/office/register")
def create_office_user(username: str = Form(...), password: str = Form(...)):
    auth_model = AuthModel(config)
    auth_model.create_office_user(username, password)
    user = auth_model.find_office_user_by_name_and_password(username, password)
    response = RedirectResponse(url="/office/menue", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


# 企業側予約確認
@app.get("/office/reservation/{date}")
@check_login
def offie_display_reservation(request: Request, date, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "office_display_reservation.html",
        {
            "request": request,
            "date": date,
            "user": user,
        },
    )


@app.get("/office/reservation/date/{date}")
@check_login
def get_data_by_date(request: Request, date, session_id=Cookie(default=None)):
    reservation_model = ReservationModel(config)
    all_reservations = reservation_model.fetch_reservation_by_date(date)
    return all_reservations


@app.get("/menue")
@check_login
def display_menue(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("menue.html", {"request": request, "user": user})


@app.get("/reserve/make")
@check_login
def select_date_time(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "reserve_date.html", {"request": request, "user": user}
    )


@app.get("/definite_reserve_date/{date}")
@check_login
def send_time(request: Request, date, session_id=Cookie(default=None)):
    reservation_model = ReservationModel(config)
    reservationTimes = reservation_model.fetch_reservation_by_date(date)
    return reservationTimes


@app.get("/make_reserve")
@check_login
def display_reserve(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    min_date = datetime.date.today()
    max_date_month = min_date.month + 1
    max_date_year = min_date.year
    max_date = "%d-0%d-31" % (max_date_year, max_date_month)
    return templates.TemplateResponse(
        "make_reserve.html",
        {"request": request, "user": user, "min_date": min_date, "max_date": max_date},
    )


@app.get("/reserve/confirm/{dateTime}")
@check_login
def display_confirm(request: Request, dateTime, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    dateTime = dateTime
    return templates.TemplateResponse(
        "confirm_reservation.html",
        {"request": request, "user": user, "dateTime": dateTime},
    )


@app.get("/reserve/sub/{dateTime}")
@check_login
def make_sub_reserve(request: Request, dateTime, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    dateTime = dateTime
    return templates.TemplateResponse(
        "confirm_sub_reservation.html",
        {"request": request, "user": user, "dateTime": dateTime},
    )


@app.get("/reserve/complete/{dateTime}")
@check_login
def display_finish(request: Request, dateTime, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    user_id = user["id"]
    reservation_model = ReservationModel(config)
    date = dateTime[0:10]
    hour = dateTime[11:13]
    time = "{}:00".format(hour)
    reservation_model.create_reservation(user_id, date, time)
    return templates.TemplateResponse(
        "display_finish.html",
        {
            "request": request,
            "user": user,
            "username": user["username"],
            "date": date,
            "time": time,
            "dateTime": dateTime,
            "reserve": "予約",
        },
    )


@app.get("/reserve/sub/complete/{dateTime}")
@check_login
def display_sub_finish(request: Request, dateTime, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    user_id = user["id"]
    reservation_model = ReservationModel(config)
    date = dateTime[0:10]
    hour = dateTime[11:13]
    time = "{}:00".format(hour)
    reservation_model.create_sub_reservation(user_id, date, time)
    return templates.TemplateResponse(
        "display_finish.html",
        {
            "request": request,
            "user": user,
            "username": user["username"],
            "date": date,
            "time": time,
            "dateTime": dateTime,
            "sub": "登録",
        },
    )


# 削除機能
@app.get("/delete_reservation/{reservation_id}")
@check_login
def delete_reservation(
    request: Request, reservation_id: int, session_id=Cookie(default=None)
):
    reservation_model = ReservationModel(config)
    reservation_model.delete_reservation_by_id(reservation_id)
    return RedirectResponse("/confirm_reserve")


@app.get("/office/delete_reservation/{reservation_id}/{date}")
@check_login
def office_delete_reservation(
    request: Request, reservation_id: int, date, session_id=Cookie(default=None)
):
    reservation_model = ReservationModel(config)
    obReservation = reservation_model.fetch_time_by_reservationid(reservation_id)
    time = obReservation["time"]
    reservation_model.delete_reservation_by_id(reservation_id)
    reservation_model.update_state(date, time)
    url = "/office/reservation/{}".format(date)
    return RedirectResponse(url)


@app.get("/{reservation_id}/{date}")
def a(request: Request, reservation_id: int, date, session_id=Cookie(default=None)):
    reservation_model = ReservationModel(config)
    obReservation = reservation_model.fetch_time_by_reservationid(reservation_id)
    time = obReservation["time"]
    return time


# 予約確認画面
@app.get("/confirm_reserve")
@check_login
def confirm_reserve(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    user_id = user["id"]
    reservation_model = ReservationModel(config)
    reservations = reservation_model.fetch_reservation_by_id(user_id)

    return templates.TemplateResponse(
        "confirm_reserve.html",
        {
            "request": request,
            "user": user,
            "reservations": reservations,
        },
    )


"""""
##予約確認画面の表示  時間の都合上削除
@app.get("/confirm_reserve")
def confirm_reserve(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("confirm_reserve.html",{
        "request": request,
        "user": user
    })
"""

# 予約入力
"""""
@app.post("/make_reverse")
@check_login
def make_reserve(date = Form(...), session_id=Cookie(default=None)):
    return RedirectResponse("/confirm_reserve", status_code=HTTP_302_FOUND)
"""


@app.post("/make_reverse")
@check_login
def make_reserve(
    request: Request, date=Form(...), time=Form(...), session_id=Cookie(default=None)
):
    user = session.get(session_id).get("user")
    user_id = user["id"]
    reservation_model = ReservationModel(config)
    reservation_model.create_reservation(user_id, date, time)

    # 以下はモジュール作成
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]

    hour = time[0:2]
    minute = time[3:5]

    # ここまで

    return templates.TemplateResponse(
        "finish_reserve.html",
        {
            "request": request,
            "user": user,
            "username": user["username"],
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "time": time,
        },
    )


@app.get("/office")
def office_index(request: Request):
    return templates.TemplateResponse("office_index.html", {"request": request})


# @app.get("/menue")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    article_model = ArticleModel(config)
    articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse(
        "menue.html", {"request": request, "articles": articles, "user": user}
    )


@app.get("/article/create")
@check_login
def create_article_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "create-article.html", {"request": request, "user": user}
    )


@app.get("/articles")
def display_articles(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "article-index.html", {"request": request, "user": user}
    )


@app.post("/article/create")
@check_login
def post_article(
    title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)
):
    article_model = ArticleModel(config)
    user_id = session.get(session_id).get("user").get("id")
    article_model.create_article(user_id, title, body)
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/article/{article_id}")
@check_login
def article_detail_page(
    request: Request, article_id: int, session_id=Cookie(default=None)
):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse(
        "article-detail.html", {"request": request, "article": article, "user": user}
    )


@app.get("/logout")
@check_login
def logout(session_id=Cookie(default=None)):
    session.destroy(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response
