from re import S
from app.models.abstract import AbstractModel


class ReservationModel(AbstractModel):
    def __init__(self, config):
        super(ReservationModel, self).__init__(config)

    def create_reservation(self, user_id, date, time):
        sql = "INSERT INTO reservations(user_id, date, time, state) VALUE (%s, %s, %s, 0);"
        self.execute(sql, user_id, date, time)

    def create_sub_reservation(self, user_id, date, time):
        sql = "INSERT INTO reservations(user_id, date, time, state) VALUE (%s, %s, %s, 1);"
        self.execute(sql, user_id, date, time)

    def fetch_reservation_by_id(self, user_id):
        sql = "SELECT reservations.id,username, date, time, state FROM reservations INNER JOIN users on users.id = reservations.user_id WHERE reservations.user_id=%s;"
        return self.fetch_all(sql, user_id)

    def delete_reservation_by_id(self, reservation_id):
        sql = "DELETE FROM reservations WHERE id = %s"
        self.execute(sql, reservation_id)

    def fetch_all_reservations(self, id=0):
        sql = "SELECT username, date, time ,reservations.id FROM reservations INNER JOIN users on users.id = reservations.user_id WHERE reservations.id >= %s;"
        return self.fetch_all(sql, id)

    def fetch_reservation_by_date(self, date):
        sql = "SELECT reservations.id,username, date, time, state FROM reservations INNER JOIN users on users.id = reservations.user_id WHERE reservations.date = %s ORDER BY time;"
        return self.fetch_all(sql, date)

    def fetch_time_by_date(self, date):
        sql = "SELECT username, time as time FROM reservations INNER JOIN users on users.id = reservations.user_id WHERE reservations.date = %s ORDER BY time;"
        return self.fetch_all(sql, date)

    def fetch_time_by_reservationid(self, id):
        sql = "SELECT reservations.id,username, date, time FROM reservations INNER JOIN users on users.id = reservations.user_id WHERE reservations.id=%s;"
        return self.fetch_one(sql, id)

    def update_state(self, date, time):
        sql = "UPDATE reservations SET state = 0 WHERE date = %s AND time = %s"
        return self.execute(sql, date, time)
