from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

print(DATA_DIR)


class PMActivity:
    def __init__(self, df):
        self.activity_timeseries = df
        self.meas_begin_datetime = None
        self.meas_begin_date = None
        self.meas_begin_time = None
        self.meas_end_datetime = None
        self.meas_end_date = None
        self.meas_end_time = None
        #
        self.meas_duration = None
        self.meas_days = None
        self.meas_minutes = None
        self.meas_minutes_to_12pm = None
        self.meas_minutes_to_12pm = None

        self._calc_time_series_props()

    def _calc_time_series_props(self):
        activity = self.activity_timeseries.loc[:, ["timestamp", "activity"]]
        self.meas_begin_datetime = activity.iloc[0, 0]
        self.meas_end_datetime = activity.iloc[-1, 0]
        self.meas_begin_date = self.meas_begin_datetime.date()
        self.meas_end_date = self.meas_end_datetime.date()
        self.meas_begin_time = self.meas_begin_datetime.time()
        self.meas_end_time = self.meas_end_datetime.time()
        self.meas_duration = self.meas_end_datetime - self.meas_begin_datetime
        self.meas_minutes = self.meas_duration.total_seconds() // 60
        self.meas_days = self.meas_minutes / 1440
        self.meas_minutes_to_12pm = (
            1440 - self.meas_begin_time.hour * 60 - self.meas_begin_time.minute
        )
        self.meas_full_days = (
            self.activity_timeseries.shape[0] - self.meas_minutes_to_12pm
        ) // 1440

    def activity_day_from_to_hour(self, day, start_hour, end_hour):
        """
        Docstring for activity_day_from_to_hour
        returns timestamp and activity for specified day, start and end hour

        :param self: Description
        :param day: considered day, 0 for initial, incomplete day
                                    1 for first full day
                                   -1 for final, incomplete day
        :param start_hour: 0 to 23
        :param end_hour: 1 to 24 (exclusive last minute)
        Example: day=0, start_hour=23, end_hour=24 returns 60 entries from
                        23:00:00 to 23:59:00
        """
        if (day > 0) and (day <= self.meas_full_days):  # one of the full days
            sta_index = self.meas_minutes_to_12pm + 1440 * (day - 1) + 60 * start_hour
            end_index = self.meas_minutes_to_12pm + 1440 * (day - 1) + 60 * end_hour - 1
        elif day == 0:  # initial, incomplete day => same logic
            sta_index = self.meas_minutes_to_12pm + 1440 * (day - 1) + 60 * start_hour
            end_index = self.meas_minutes_to_12pm + 1440 * (day - 1) + 60 * end_hour - 1
        elif day == -1:  # final, incomplete day
            sta_index = (
                self.meas_minutes_to_12pm + 1440 * self.meas_full_days + 60 * start_hour
            )
            end_index = (
                self.meas_minutes_to_12pm
                + 1440 * self.meas_full_days
                + 60 * end_hour
                - 1
            )
        else:
            print("ERROR: No data for this time range...")
            return None
        if sta_index < 0 or end_index >= self.activity_timeseries.shape[0]:
            print("ERROR: No data for this time range...")
            return None
        else:
            return self.activity_timeseries.loc[
                sta_index:end_index, ["timestamp", "activity"]
            ]

    def ordered_activities(self, start_hour=0, end_hour=24):
        """
        returns a list if
        :param self: Description
        :param sta_hour: Description
        :param end_hour: Description
        """
        o_a_list_all_days = {}
        for day in range(self.meas_full_days + 2):
            df = self.activity_day_from_to_hour(self, start_hour, end_hour)
            if df is not None:
                o_a_list_day = sorted(df.loc[start_index:end_index, "activity"])
                o_a_list_all_days[day] = o_a_list_day
        return o_a_list_all_days

    def ordered_activity_24h(self, day=0, offset_minutes=0):
        start_index = 1440 * day + offset_minutes
        end_index = 1440 * (day + 1) + offset_minutes
        return sorted(
            self.activity_timeseries.loc[start_index:end_index, "activity"],
            reverse=True,
        )

    def ordered_activity_0am12pm(self, day=0):
        start_index = 1440 * day + self.meas_minutes_to_12pm + 0 * 60
        end_index = 1440 * day + self.meas_minutes_to_12pm + 24 * 60
        return sorted(
            self.activity_timeseries.loc[start_index:end_index, "activity"],
            reverse=True,
        )

    def plot_ordered_activity_24h(self, ax, data_id):
        import math

        for day in range(math.floor(self.meas_days)):
            ax.plot(self.ordered_activity_24h(day, 0), label=f"day {day}")
            ax.legend(fontsize=2, handlelength=1, labelspacing=0.3)
            ax.set_title(data_id)

    def plot_ordered_activity_8am10pm(self, ax, data_id):
        import math

        for day in range(math.floor(self.meas_days) - 1):
            ax.plot(self.ordered_activity_8am10pm(day, 0), label=f"day {day}")
            ax.legend(fontsize=2, handlelength=1, labelspacing=0.3)
            ax.set_title(data_id)


class PMAPerson:
    def __init__(self, id):
        self.id = id
        self.age = None
        self.gender = None
        self.activity = None

    def __repr__(self):
        return f"id={self.id} age={self.age}"


class PMADataADHDKaggle(PMAPerson):
    def __init__(self, id):
        self.id = id
        self.get_props()

    def get_props(self):
        self.diag = self.id.split("_")[0]
        self.datapath_raw = DATA_DIR / "raw" / "psychiatric-motor-activity-dataset"
        self.file_csv_person = self.datapath_raw / f"{self.diag}-info.csv"

        import pandas as pd

        df_person = pd.read_csv(self.file_csv_person)
        mask = df_person.loc[:, "number"] == self.id
        df_person = df_person.loc[mask, ["number", "gender", "age", "acc_time", "days"]]
        agebin = df_person.loc[:, "age"].str.split("-").iloc[0]
        self.agemin = int(agebin[0])
        self.agemax = int(agebin[1])
        self.age = (self.agemax + self.agemin) // 2
        self.gender = df_person["gender"]

        df = self.get_activity()
        self.activity = PMActivity(df)

    def get_activity(self):
        self.file_csv_activity = self.datapath_raw / self.diag / f"{self.id}.csv"
        import pandas as pd

        df = pd.read_csv(self.file_csv_activity, parse_dates=["timestamp"])
        return df


if __name__ == "__main__":
    p = PMADataADHDKaggle("control_1")
    print(p.age)
    print(p.diag)

    # some code for tests
    dir_data_raw = "../../data/raw/psychiatric-motor-activity-dataset/"
    dis = "adhd"
    print(dis)
    # dis = 'depression'
    # dis = 'schizophrenia'
    # dis = 'clinic'
    # dis = 'control'
    pat = "1"
    # import os
    # os.listdir(dir_data_raw + dis + '/')
    # filename=#
    import pandas as pd

    acty_rawfile = dir_data_raw + dis + "/" + dis + "_" + pat + ".csv"
    df = pd.read_csv(acty_rawfile, parse_dates=["timestamp"])
    print(df.head())

    bla = PMActivity(df)
    print(type(bla.meas_begin_time.minute))
    print(bla.meas_end_datetime)
    print(bla.meas_duration.days)
    print(bla.meas_duration)
    print(bla.meas_days)
    print(bla.meas_minutes)
    print(bla.meas_minutes_to_12pm)

    print(bla.ordered_activity_24h()[0:20])
