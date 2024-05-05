from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self._year = None
        self._summary = None
        self._employee_id = None
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, str):
            try:
                year = int(year)
            except ValueError:
                raise ValueError("Year should be a string representing an integer >= 2000 or an integer >= 2000")

        if not isinstance(year, int) or year < 2000:
            raise ValueError("Year should be an integer >= 2000")
        self._year = year
        
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if not summary:
            raise ValueError("Summary should be a non-empty string")
        self._summary = summary

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if not isinstance(employee_id, int):
            raise ValueError("Employee ID should be an integer")
        CURSOR.execute("SELECT id FROM employees WHERE id = ?", (employee_id,))
        data = CURSOR.fetchone()
        if data is None:
            raise ValueError("Employee ID should be the id of an Employee that exists in the 'employees' table")
        self._employee_id = employee_id

    # ... existing methods ...

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id),
            )
            self.id = CURSOR.lastrowid
            self.__class__.all[self.id] = self
        else:
            CURSOR.execute(
                "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
                (self.year, self.summary, self.employee_id, self.id),
            )
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Create a Review instance from a database row"""
        return cls(row[1], row[2], row[3], row[0])

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id),
        )
        CONN.commit()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        del self.__class__.all[self.id]
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()
        
    @classmethod
    def drop_table(cls):
        """ Drop the "reviews" table """
        sql = """
            DROP TABLE IF EXISTS reviews
        """
        CURSOR.execute(sql)
        CONN.commit()